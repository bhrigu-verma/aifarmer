from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.crop import Crop, CropStage
from app.schemas.crop import CropRecommendation, CropAdvisorResponse, InputRecommendation


CROP_DATA = [
    {
        "name": "Wheat", "name_hi": "गेहूं", "season": "rabi",
        "suitable_soils": ["alluvial", "loamy", "clay"],
        "yield": 18, "cost": 15000, "revenue": 36000, "risk": "low",
        "risk_text": "Stable demand, government MSP support",
        "risk_text_hi": "स्थिर मांग, सरकारी MSP समर्थन",
    },
    {
        "name": "Rice", "name_hi": "धान", "season": "kharif",
        "suitable_soils": ["alluvial", "clay", "loamy"],
        "yield": 25, "cost": 20000, "revenue": 50000, "risk": "low",
        "risk_text": "High water requirement but stable market",
        "risk_text_hi": "पानी की अधिक जरूरत लेकिन स्थिर बाजार",
    },
    {
        "name": "Cotton", "name_hi": "कपास", "season": "kharif",
        "suitable_soils": ["black", "alluvial", "loamy"],
        "yield": 8, "cost": 25000, "revenue": 48000, "risk": "medium",
        "risk_text": "Vulnerable to bollworm, price fluctuations",
        "risk_text_hi": "बॉलवर्म और कीमत में उतार-चढ़ाव का खतरा",
    },
    {
        "name": "Soybean", "name_hi": "सोयाबीन", "season": "kharif",
        "suitable_soils": ["black", "loamy", "alluvial"],
        "yield": 10, "cost": 12000, "revenue": 35000, "risk": "medium",
        "risk_text": "Weather sensitive, moderate returns",
        "risk_text_hi": "मौसम पर निर्भर, मध्यम रिटर्न",
    },
    {
        "name": "Mustard", "name_hi": "सरसों", "season": "rabi",
        "suitable_soils": ["loamy", "sandy", "alluvial"],
        "yield": 8, "cost": 10000, "revenue": 28000, "risk": "low",
        "risk_text": "Low input cost, drought tolerant",
        "risk_text_hi": "कम लागत, सूखा सहनशील",
    },
    {
        "name": "Sugarcane", "name_hi": "गन्ना", "season": "kharif",
        "suitable_soils": ["alluvial", "loamy", "black"],
        "yield": 350, "cost": 50000, "revenue": 120000, "risk": "medium",
        "risk_text": "High water use, delayed mill payments",
        "risk_text_hi": "पानी की अधिक खपत, मिल भुगतान में देरी",
    },
    {
        "name": "Chickpea", "name_hi": "चना", "season": "rabi",
        "suitable_soils": ["loamy", "sandy", "red"],
        "yield": 8, "cost": 10000, "revenue": 32000, "risk": "low",
        "risk_text": "Good pulse crop with MSP, low water need",
        "risk_text_hi": "MSP समर्थन वाली अच्छी दाल फसल, कम पानी",
    },
    {
        "name": "Tomato", "name_hi": "टमाटर", "season": "kharif",
        "suitable_soils": ["loamy", "red", "alluvial"],
        "yield": 100, "cost": 40000, "revenue": 100000, "risk": "high",
        "risk_text": "Very high price volatility, perishable",
        "risk_text_hi": "कीमत में बहुत उतार-चढ़ाव, जल्दी खराब होता है",
    },
    {
        "name": "Potato", "name_hi": "आलू", "season": "rabi",
        "suitable_soils": ["sandy", "loamy", "alluvial"],
        "yield": 100, "cost": 35000, "revenue": 60000, "risk": "medium",
        "risk_text": "Needs cold storage, price drops in glut",
        "risk_text_hi": "कोल्ड स्टोरेज जरूरी, अधिक उत्पादन में दाम गिरते हैं",
    },
    {
        "name": "Maize", "name_hi": "मक्का", "season": "kharif",
        "suitable_soils": ["loamy", "alluvial", "red"],
        "yield": 25, "cost": 12000, "revenue": 30000, "risk": "low",
        "risk_text": "Growing demand for animal feed and starch",
        "risk_text_hi": "पशु चारे और स्टार्च के लिए बढ़ती मांग",
    },
]


def get_current_season() -> str:
    from datetime import datetime
    month = datetime.now().month
    if month in (6, 7, 8, 9, 10):
        return "kharif"
    elif month in (11, 12, 1, 2, 3):
        return "rabi"
    else:
        return "zaid"


def recommend_crops(
    soil_type: str,
    season: Optional[str] = None,
    land_size_acres: float = 1.0,
) -> CropAdvisorResponse:
    if not season:
        season = get_current_season()

    scored: List[dict] = []
    for crop in CROP_DATA:
        if crop["season"] != season:
            continue
        soil_match = soil_type.lower() in crop["suitable_soils"]
        score = 0
        if soil_match:
            score += 50
        profit = crop["revenue"] - crop["cost"]
        if profit > 20000:
            score += 30
        elif profit > 10000:
            score += 20
        else:
            score += 10
        if crop["risk"] == "low":
            score += 20
        elif crop["risk"] == "medium":
            score += 10

        scored.append({"crop": crop, "score": score, "profit": profit})

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:3]

    recommendations = []
    for item in top:
        c = item["crop"]
        recommendations.append(
            CropRecommendation(
                crop_name=c["name"],
                crop_name_hi=c["name_hi"],
                season=c["season"],
                expected_yield_per_acre=c["yield"],
                expected_cost_per_acre=c["cost"],
                expected_revenue_per_acre=c["revenue"],
                expected_profit_per_acre=item["profit"],
                risk_level=c["risk"],
                risk_explanation=c["risk_text"],
                risk_explanation_hi=c["risk_text_hi"],
                suitability_score=item["score"],
            )
        )

    return CropAdvisorResponse(
        farmer_state="",
        farmer_district="",
        soil_type=soil_type,
        season=season,
        recommendations=recommendations,
    )


INPUT_STAGES = {
    "wheat": [
        {"stage": "Land Preparation", "order": 1, "days": 15, "fert": "DAP", "fert_qty": 50, "water_freq": 0, "water_qty": 0, "pest": None, "pest_qty": 0, "care": "Plough 2-3 times, level the field", "care_hi": "2-3 बार जुताई करें, खेत समतल करें", "cost": 3000},
        {"stage": "Sowing", "order": 2, "days": 7, "fert": "Urea", "fert_qty": 25, "water_freq": 7, "water_qty": 5000, "pest": None, "pest_qty": 0, "care": "Sow seeds at 20cm row spacing", "care_hi": "20cm कतार में बीज बोएं", "cost": 4000},
        {"stage": "Tillering", "order": 3, "days": 30, "fert": "Urea", "fert_qty": 30, "water_freq": 15, "water_qty": 6000, "pest": None, "pest_qty": 0, "care": "First irrigation 21 days after sowing", "care_hi": "बुवाई के 21 दिन बाद पहली सिंचाई", "cost": 2000},
        {"stage": "Flowering", "order": 4, "days": 20, "fert": None, "fert_qty": 0, "water_freq": 10, "water_qty": 5000, "pest": "Propiconazole", "pest_qty": 200, "care": "Watch for rust disease", "care_hi": "रतुआ रोग पर नजर रखें", "cost": 2500},
        {"stage": "Harvesting", "order": 5, "days": 10, "fert": None, "fert_qty": 0, "water_freq": 0, "water_qty": 0, "pest": None, "pest_qty": 0, "care": "Harvest when grain moisture is 12-14%", "care_hi": "जब दाने में नमी 12-14% हो तब कटाई करें", "cost": 3500},
    ],
    "rice": [
        {"stage": "Nursery", "order": 1, "days": 25, "fert": "DAP", "fert_qty": 10, "water_freq": 2, "water_qty": 3000, "pest": None, "pest_qty": 0, "care": "Prepare raised nursery bed", "care_hi": "उठी हुई नर्सरी क्यारी तैयार करें", "cost": 2000},
        {"stage": "Transplanting", "order": 2, "days": 7, "fert": "Urea", "fert_qty": 30, "water_freq": 3, "water_qty": 8000, "pest": None, "pest_qty": 0, "care": "Transplant 25-day old seedlings", "care_hi": "25 दिन पुरानी पौध रोपें", "cost": 5000},
        {"stage": "Vegetative", "order": 3, "days": 40, "fert": "Urea", "fert_qty": 40, "water_freq": 5, "water_qty": 10000, "pest": "Chlorpyrifos", "pest_qty": 500, "care": "Maintain 5cm standing water", "care_hi": "5cm खड़ा पानी बनाए रखें", "cost": 4000},
        {"stage": "Flowering", "order": 4, "days": 25, "fert": "MOP", "fert_qty": 20, "water_freq": 4, "water_qty": 8000, "pest": "Tricyclazole", "pest_qty": 300, "care": "Control blast disease", "care_hi": "ब्लास्ट रोग नियंत्रित करें", "cost": 3000},
        {"stage": "Harvesting", "order": 5, "days": 10, "fert": None, "fert_qty": 0, "water_freq": 0, "water_qty": 0, "pest": None, "pest_qty": 0, "care": "Drain field 15 days before harvest", "care_hi": "कटाई से 15 दिन पहले पानी निकालें", "cost": 4000},
    ],
}


def get_input_recommendation(crop_name: str) -> List[InputRecommendation]:
    stages = INPUT_STAGES.get(crop_name.lower(), [])
    if not stages:
        return [
            InputRecommendation(
                crop_name=crop_name,
                stage_name="General",
                fertiliser_type="NPK",
                fertiliser_quantity_kg_per_acre=50,
                water_frequency_days=7,
                water_quantity_litres_per_acre=5000,
                pesticide_name=None,
                pesticide_quantity_ml_per_acre=None,
                care_instructions="Follow local agricultural extension advice",
                care_instructions_hi="स्थानीय कृषि विस्तार सलाह का पालन करें",
                estimated_cost=15000,
            )
        ]

    return [
        InputRecommendation(
            crop_name=crop_name,
            stage_name=s["stage"],
            fertiliser_type=s["fert"],
            fertiliser_quantity_kg_per_acre=s["fert_qty"] if s["fert_qty"] else None,
            water_frequency_days=s["water_freq"] if s["water_freq"] else None,
            water_quantity_litres_per_acre=s["water_qty"] if s["water_qty"] else None,
            pesticide_name=s["pest"],
            pesticide_quantity_ml_per_acre=s["pest_qty"] if s["pest_qty"] else None,
            care_instructions=s["care"],
            care_instructions_hi=s["care_hi"],
            estimated_cost=s["cost"],
        )
        for s in stages
    ]
