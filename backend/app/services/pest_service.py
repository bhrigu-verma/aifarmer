from typing import Optional

from app.schemas.pest import PestDetectionResult


DISEASE_DATABASE = {
    "leaf_blight": PestDetectionResult(
        disease_name="Leaf Blight",
        disease_name_hi="पत्ती झुलसा",
        confidence=0.0,
        crop_name="Rice",
        description="Bacterial leaf blight causes wilting and yellowing of leaves",
        description_hi="जीवाणु पत्ती झुलसा से पत्तियां मुरझाती और पीली हो जाती हैं",
        treatment=["Apply Streptocycline 0.01%", "Spray Copper oxychloride 0.25%", "Drain excess water"],
        treatment_hi=["स्ट्रेप्टोसाइक्लिन 0.01% लगाएं", "कॉपर ऑक्सीक्लोराइड 0.25% स्प्रे करें", "अतिरिक्त पानी निकालें"],
        products_available=["Streptocycline", "Blitox-50", "COC 50% WP"],
        severity="moderate",
        prevention_tips=["Use resistant varieties", "Avoid excess nitrogen", "Ensure proper drainage"],
    ),
    "powdery_mildew": PestDetectionResult(
        disease_name="Powdery Mildew",
        disease_name_hi="चूर्णी फफूंदी",
        confidence=0.0,
        crop_name="Wheat",
        description="White powdery fungal growth on leaves and stems",
        description_hi="पत्तियों और तनों पर सफेद चूर्णी कवक वृद्धि",
        treatment=["Spray Karathane 0.05%", "Apply Sulphur dust 25-30 kg/ha", "Use Propiconazole 0.1%"],
        treatment_hi=["कैराथेन 0.05% स्प्रे करें", "सल्फर डस्ट 25-30 kg/हेक्टेयर लगाएं", "प्रोपिकोनाजोल 0.1% का उपयोग करें"],
        products_available=["Karathane", "Sulphur WP", "Tilt (Propiconazole)"],
        severity="mild",
        prevention_tips=["Grow resistant varieties", "Avoid late sowing", "Proper spacing"],
    ),
    "late_blight": PestDetectionResult(
        disease_name="Late Blight",
        disease_name_hi="पछेती झुलसा",
        confidence=0.0,
        crop_name="Potato",
        description="Dark brown lesions on leaves, white fungal growth underneath",
        description_hi="पत्तियों पर गहरे भूरे धब्बे, नीचे सफेद कवक वृद्धि",
        treatment=["Spray Mancozeb 0.25%", "Apply Metalaxyl-Mancozeb", "Remove infected plants"],
        treatment_hi=["मैंकोजेब 0.25% स्प्रे करें", "मेटालैक्सिल-मैंकोजेब लगाएं", "संक्रमित पौधे हटाएं"],
        products_available=["Dithane M-45", "Ridomil Gold", "Curzate"],
        severity="severe",
        prevention_tips=["Use certified seed", "Plant resistant varieties", "Avoid excess irrigation"],
    ),
    "bollworm": PestDetectionResult(
        disease_name="Bollworm",
        disease_name_hi="बॉलवर्म (डोडा कीट)",
        confidence=0.0,
        crop_name="Cotton",
        description="Larvae bore into cotton bolls, causing significant yield loss",
        description_hi="लार्वा कपास के डोडों में छेद करते हैं, जिससे उपज में भारी नुकसान",
        treatment=["Install pheromone traps", "Spray Emamectin benzoate 5% SG", "Use Neem oil 5%"],
        treatment_hi=["फेरोमोन ट्रैप लगाएं", "इमामेक्टिन बेंजोएट 5% SG स्प्रे करें", "नीम तेल 5% का उपयोग करें"],
        products_available=["Proclaim (Emamectin)", "Neem oil", "Pheromone traps"],
        severity="severe",
        prevention_tips=["Plant Bt cotton varieties", "Maintain refuge crop", "Monitor with traps from 60 DAS"],
    ),
    "rust": PestDetectionResult(
        disease_name="Rust",
        disease_name_hi="रतुआ",
        confidence=0.0,
        crop_name="Wheat",
        description="Orange-brown pustules on leaves and stems reducing photosynthesis",
        description_hi="पत्तियों और तनों पर नारंगी-भूरे दाने जो प्रकाश संश्लेषण कम करते हैं",
        treatment=["Spray Propiconazole 25EC at 0.1%", "Apply Mancozeb 75WP", "Two sprays at 15 day interval"],
        treatment_hi=["प्रोपिकोनाजोल 25EC 0.1% पर स्प्रे करें", "मैंकोजेब 75WP लगाएं", "15 दिन के अंतराल पर दो स्प्रे"],
        products_available=["Tilt 25EC", "Dithane M-45", "Bavistin"],
        severity="moderate",
        prevention_tips=["Grow rust-resistant varieties", "Timely sowing", "Balanced fertiliser use"],
    ),
}


def detect_disease(image_description: str = "") -> PestDetectionResult:
    """Placeholder for ML-based disease detection.
    In production, this would accept an image, run it through a trained model,
    and return the detected disease. For now, returns a sample result.
    """
    result = DISEASE_DATABASE["leaf_blight"].model_copy()
    result.confidence = 0.85
    return result


def get_disease_info(disease_key: str) -> Optional[PestDetectionResult]:
    return DISEASE_DATABASE.get(disease_key)


def list_known_diseases() -> list[str]:
    return list(DISEASE_DATABASE.keys())
