# Farmer Scenarios — AI Farmer Assistant

Five realistic, end-to-end farmer scenario walkthroughs that test every major feature of the AI Farmer Assistant app. Each scenario follows a real farmer persona through a complete farming cycle.

---

## Scenario 1: Ramu — Rabi Season Crop Selection in Madhya Pradesh

### Farmer Profile

| Detail | Value |
|--------|-------|
| **Name** | Ramu Patel |
| **Location** | Village Bhopalpur, District Sehore, Madhya Pradesh |
| **Land** | 3 acres (owned) |
| **Soil Type** | Black (Regur/Cotton) soil |
| **Irrigation** | Borewell (seasonal availability) |
| **Phone** | Redmi 9A, Android 10, patchy 4G |
| **Language** | Hindi |
| **Experience** | 15 years; grew soybean (kharif) just completed |

### Problem Statement

Ramu just finished harvesting soybean. He needs to decide what to sow for the rabi season. Last year he grew wheat but got a low price because everyone in his area grew wheat. He wants to make more money this season.

### Walkthrough

#### Step 1: Registration

```
Action: Ramu downloads the app from Play Store (18 MB)
Screen: Language selection → Hindi selected
Screen: Registration form (voice-assisted)

API Call: POST /api/v1/farmers/
Payload:
{
  "name": "रामू पटेल",
  "phone": "9826XXXXXX",
  "state": "Madhya Pradesh",
  "district": "Sehore",
  "village": "Bhopalpur",
  "latitude": 23.2,
  "longitude": 77.08,
  "land_size_acres": 3.0,
  "soil_type": "black",
  "irrigation_source": "borewell",
  "language": "hi"
}

Response: 201 Created — Farmer registered with id: 1
```

#### Step 2: Get Crop Recommendation

```
Action: Ramu taps "फसल सलाह" (Crop Advisor) icon
Screen: Shows his pre-filled soil type and auto-detected season (rabi)

API Call: GET /api/v1/crops/recommend?soil_type=black&season=rabi&land_size_acres=3
Response:
{
  "recommendations": [
    {
      "name": "Chickpea",
      "name_hi": "चना",
      "season": "rabi",
      "avg_cost_per_acre": 8000,
      "avg_revenue_per_acre": 22000,
      "profit_per_acre": 14000,
      "risk_level": "low",
      "suitability_score": 92,
      "reason": "Black soil ideal for chickpea. MSP guaranteed at ₹5,440/quintal."
    },
    {
      "name": "Wheat",
      "name_hi": "गेहूं",
      "suitability_score": 85,
      "profit_per_acre": 13000,
      "risk_level": "low"
    },
    {
      "name": "Mustard",
      "name_hi": "सरसों",
      "suitability_score": 70,
      "profit_per_acre": 12000,
      "risk_level": "medium"
    }
  ]
}

Display: Cards showing each crop with profit, risk level, and suitability in Hindi
Ramu's Decision: Chooses Chickpea (चना) — highest suitability, MSP-backed
```

#### Step 3: Get Input Guide for Chickpea

```
Action: Ramu taps "Know More" on Chickpea card
API Call: GET /api/v1/crops/inputs/chickpea
Response: Stage-by-stage guide
  - Stage 1: Land preparation — ploughing, seed treatment
  - Stage 2: Sowing — 30kg seed/acre, row spacing 30cm
  - Stage 3: Irrigation — first at 30 days, then at flowering
  - Stage 4: Pest watch — pod borer monitoring from week 8
  - Stage 5: Harvest — at 90-100 days when pods turn brown

Display: Visual timeline with icons for each stage
Action: Ramu saves this to offline (auto-cached)
```

#### Step 4: Check Weather Before Sowing

```
Action: Ramu checks weather before sowing (November 5)
API Call: GET /api/v1/weather/forecast?latitude=23.2&longitude=77.08&days=10
Response:
{
  "forecast": [
    {"date": "2024-11-05", "temp_max": 32, "temp_min": 18, "precipitation": 0, "description": "Clear sky"},
    {"date": "2024-11-06", "temp_max": 31, "temp_min": 17, "precipitation": 0, "description": "Partly cloudy"},
    ...
    {"date": "2024-11-09", "temp_max": 28, "temp_min": 15, "precipitation": 2, "description": "Light rain"}
  ]
}

API Call: GET /api/v1/weather/alerts?latitude=23.2&longitude=77.08&crop=chickpea
Response: { "alerts": [] }  ← No weather alerts, safe to sow

Decision: Ramu plans to sow on November 7 (clear weather window)
```

#### Step 5: Record Sowing in Diary

```
Action: After sowing, Ramu records the expense
API Call: POST /api/v1/diary/1
Payload:
{
  "crop_name": "Chickpea",
  "activity": "Sowing - 90kg seed purchased and sown",
  "category": "sowing",
  "expense_amount": 5400,
  "season": "rabi-2024"
}

Response: 201 Created — Entry saved (also saved to local SQLite)
```

#### Step 6: Check Government Schemes

```
Action: Ramu taps "सरकारी योजनाएं" (Government Schemes)
API Call: GET /api/v1/schemes/?state=Madhya Pradesh&land_size_acres=3&farmer_name=रामू पटेल
Response: Shows 6 eligible schemes including:
  - PM-KISAN: ₹6,000/year (Ramu learns he hasn't claimed last installment)
  - PMFBY: Ramu decides to insure his chickpea crop (premium: 1.5%)
  - KCC: Ramu considers applying for credit card

Result: Ramu calls the helpline (1800-180-1551) to check his PM-KISAN status
```

### Features Tested
✅ Farmer registration, ✅ Crop recommendation, ✅ Input guide, ✅ Weather forecast, ✅ Weather alerts, ✅ Crop diary, ✅ Government schemes, ✅ Hindi language, ✅ Offline caching

---

## Scenario 2: Lakshmi — Cotton Disease Emergency in Maharashtra

### Farmer Profile

| Detail | Value |
|--------|-------|
| **Name** | Lakshmi Jadhav |
| **Location** | Village Pimpalgaon, District Yavatmal, Maharashtra |
| **Land** | 5 acres (owned) |
| **Soil Type** | Black soil |
| **Irrigation** | Rainfed (no irrigation source) |
| **Phone** | Samsung Galaxy M02, Android 10 |
| **Language** | Marathi (uses Hindi in app) |
| **Current Crop** | BT Cotton, planted June 2024, now in flowering stage |

### Problem Statement

Lakshmi notices white powdery spots on her cotton leaves. She doesn't know what it is. The nearest agricultural office is 40km away. She needs diagnosis and treatment advice immediately.

### Walkthrough

#### Step 1: Disease Detection

```
Action: Lakshmi opens app → taps "रोग पहचान" (Disease Detection)
Screen: Camera opens
Action: She photographs the affected cotton leaf (close-up of white spots)

API Call: POST /api/v1/pests/detect
Body: multipart/form-data with image file (JPEG, compressed to ~200KB)

Response:
{
  "disease_name": "Powdery Mildew",
  "disease_name_hi": "चूर्णिल फफूंदी",
  "confidence": 0.85,
  "crop": "Cotton",
  "severity": "mild",
  "description": "Fungal infection causing white powdery coating on leaves",
  "treatment": [
    "Spray Sulphur WP 80% at 2g/litre water",
    "Apply Karathane (Dinocap) at 1ml/litre as second spray"
  ],
  "products": [
    {"name": "Sulphur WP 80%", "dosage": "2g/litre", "approx_cost": "₹180/500g"},
    {"name": "Karathane 48EC", "dosage": "1ml/litre", "approx_cost": "₹350/250ml"}
  ],
  "prevention_tips": [
    "Avoid excessive nitrogen fertiliser",
    "Ensure adequate plant spacing for air circulation",
    "Remove and destroy severely infected leaves"
  ]
}

Display: Shows disease name (Hindi), photo comparison, treatment steps, nearby dealer info
```

#### Step 2: Check Weather for Spray Timing

```
Action: Lakshmi needs to spray fungicide — checks weather for dry window
API Call: GET /api/v1/weather/forecast?latitude=20.39&longitude=78.12&days=5
Response:
  Nov 10: Clear, 30°C — ✅ Good spray day
  Nov 11: Partly cloudy, 29°C — ✅ Acceptable
  Nov 12: Rain expected, 25°C — ❌ Don't spray
  Nov 13: Rain, 24°C — ❌ Don't spray
  Nov 14: Clear, 28°C — ✅ Second spray possible

Decision: Lakshmi sprays on Nov 10 (morning, before 10 AM as advised)
```

#### Step 3: Record Expense

```
API Call: POST /api/v1/diary/2
Payload:
{
  "crop_name": "Cotton",
  "activity": "Powdery mildew treatment - Sulphur WP spray",
  "category": "pesticide",
  "expense_amount": 800,
  "notes": "2 sprays planned. First spray done Nov 10.",
  "season": "kharif-2024"
}
```

#### Step 4: Follow-up — Disease Reference

```
Action: Two weeks later, Lakshmi wants to check if the disease is recurring
API Call: GET /api/v1/pests/diseases/powdery_mildew
Response: Full disease profile with prevention calendar, resistant varieties info

Action: She also photographs a different symptom
API Call: POST /api/v1/pests/detect (new image)
Response: "Bollworm" detected with severe rating
  - Treatment: Spray Profenophos 50EC at 2ml/litre
  - Urgency: Immediate — bollworm can destroy 30-50% of bolls

Action: Records bollworm treatment expense (₹1,200)
```

#### Step 5: Season Summary

```
Action: At end of season, Lakshmi checks her profitability
API Call: GET /api/v1/diary/2/summary?season=kharif-2024&crop_name=Cotton
Response:
{
  "total_expenses": 42000,
  "total_income": 67000,
  "net_profit": 25000,
  "expense_breakdown": {
    "sowing": 8000,
    "fertiliser": 12000,
    "pesticide": 6500,
    "irrigation": 0,
    "labour": 10000,
    "harvest": 5500
  }
}

Insight: Lakshmi sees pesticide costs were ₹6,500 — if she had caught powdery mildew
earlier, she could have saved ₹2,000+ in treatment costs.
```

### Features Tested
✅ Disease detection (image upload), ✅ Disease database lookup, ✅ Weather for spray timing, ✅ Crop diary (multiple entries), ✅ Season summary with breakdown, ✅ Offline detection capability

---

## Scenario 3: Gurpreet — Wheat Selling Strategy in Punjab

### Farmer Profile

| Detail | Value |
|--------|-------|
| **Name** | Gurpreet Singh |
| **Location** | Village Phillaur, District Jalandhar, Punjab |
| **Land** | 8 acres (owned) |
| **Soil Type** | Alluvial |
| **Irrigation** | Canal + tubewell |
| **Phone** | Xiaomi Redmi Note 9, Android 11, good 4G |
| **Language** | Punjabi (uses Hindi in app) |
| **Current Situation** | Wheat harvest completed (April), has 60 quintals in storage |

### Problem Statement

Gurpreet has harvested 60 quintals of wheat. The MSP is ₹2,275/quintal but the local mandi is offering ₹2,100. He's wondering whether to sell now, wait for MSP procurement, or try a different mandi.

### Walkthrough

#### Step 1: Check Mandi Prices

```
Action: Gurpreet opens app → taps "मंडी भाव" (Mandi Prices)
API Call: GET /api/v1/mandi/prices?crop_name=wheat&state=Punjab

Response:
[
  {"mandi_name": "Jalandhar", "modal_price": 2100, "min_price": 2000, "max_price": 2200, "price_date": "2024-04-10"},
  {"mandi_name": "Ludhiana", "modal_price": 2250, "min_price": 2150, "max_price": 2350, "price_date": "2024-04-10"},
  {"mandi_name": "Amritsar", "modal_price": 2180, "min_price": 2050, "max_price": 2275, "price_date": "2024-04-10"},
  {"mandi_name": "Phagwara", "modal_price": 2150, "min_price": 2050, "max_price": 2250, "price_date": "2024-04-10"},
  {"mandi_name": "Khanna", "modal_price": 2275, "min_price": 2200, "max_price": 2350, "price_date": "2024-04-10"}
]

Display: Price comparison cards showing all mandis, sorted by modal price
Key Insight: Khanna mandi is paying MSP (₹2,275) — Ludhiana also near MSP
```

#### Step 2: Price Trend Analysis

```
Action: Gurpreet checks 30-day trend for Jalandhar mandi
API Call: GET /api/v1/mandi/trend?crop_name=wheat&mandi_name=Jalandhar&days=30

Response:
{
  "crop_name": "Wheat",
  "mandi_name": "Jalandhar",
  "prices": [...30 daily prices...],
  "trend": "rising",
  "trend_percentage": 7.2,
  "recommendation": "Prices are trending upward. Consider waiting for better rates.",
  "recommendation_hi": "भाव बढ़ रहे हैं। बेहतर दाम के लिए इंतज़ार करें।"
}
```

#### Step 3: Get Sell Recommendation

```
API Call: GET /api/v1/mandi/sell-recommendation?crop_name=wheat&mandi_name=Jalandhar&msp_price=2275

Response:
{
  "current_price": 2100,
  "avg_30_day_price": 2020,
  "msp_price": 2275,
  "recommendation": "wait",
  "reasoning": "Current price (₹2,100) is above 30-day average (₹2,020) and trending up. Government MSP procurement at ₹2,275 starts April 15. Recommend waiting for MSP procurement or selling at Khanna mandi where MSP price is already being offered.",
  "reasoning_hi": "मौजूदा भाव (₹2,100) 30 दिन के औसत (₹2,020) से ऊपर है और बढ़ रहा है। सरकारी MSP खरीद ₹2,275 पर 15 अप्रैल से शुरू होगी। MSP खरीद का इंतज़ार करें या खन्ना मंडी में बेचें जहां MSP भाव मिल रहा है।"
}
```

#### Step 4: Decision and Sale

```
Decision: Gurpreet decides to:
  - Sell 30 quintals at Khanna mandi NOW (₹2,275 × 30 = ₹68,250)
  - Wait for MSP procurement for remaining 30 quintals

Action: Records the sale
API Call: POST /api/v1/diary/3
Payload:
{
  "crop_name": "Wheat",
  "activity": "Sold 30 quintals at Khanna mandi at MSP rate",
  "category": "sale",
  "income_amount": 68250,
  "expense_amount": 1500,
  "notes": "Transport cost ₹1,500 to Khanna. Remaining 30 quintals waiting for MSP procurement.",
  "season": "rabi-2024"
}
```

#### Step 5: Profit Calculation

```
API Call: GET /api/v1/diary/3/summary?season=rabi-2024&crop_name=Wheat
Response:
{
  "total_expenses": 98000,
  "total_income": 136500,
  "net_profit": 38500,
  "expense_breakdown": {
    "sowing": 12000,
    "fertiliser": 18000,
    "irrigation": 8000,
    "pesticide": 4000,
    "labour": 20000,
    "harvest": 14000,
    "sale": 1500,
    "other": 500
  }
}

Comparison: If Gurpreet had sold all 60 quintals at Jalandhar (₹2,100):
  Revenue = 60 × 2,100 = ₹1,26,000
  By using the app: ₹1,36,500 (sold 30 at ₹2,275 + 30 at ₹2,275 MSP)
  Extra earning: ₹10,500 from one season, one crop
```

### Features Tested
✅ Mandi price comparison (multi-mandi), ✅ Price trend analysis, ✅ Sell/wait/hold recommendation, ✅ MSP comparison, ✅ Diary income recording, ✅ Season summary, ✅ Multi-language recommendations

---

## Scenario 4: Anitha — First-Time App User in Tamil Nadu (Low Connectivity)

### Farmer Profile

| Detail | Value |
|--------|-------|
| **Name** | Anitha Murugan |
| **Location** | Village Keeranur, District Pudukkottai, Tamil Nadu |
| **Land** | 1.5 acres (owned) |
| **Soil Type** | Red soil |
| **Irrigation** | Rainfed + small farm pond |
| **Phone** | Nokia C01 Plus, Android 11 Go, 2GB RAM, mostly 2G |
| **Language** | Tamil (app fallback: Hindi) |
| **Literacy** | Semi-literate; relies on voice and icons |

### Problem Statement

Anitha is a smallholder farmer growing millets and vegetables. She heard about the app from a Farmer Producer Organization (FPO) meeting. She has unreliable internet (2G most of the time, brief 4G windows when she goes to town). She needs the app to work even without connectivity.

### Walkthrough

#### Step 1: Initial Setup (at FPO office with WiFi)

```
Action: FPO coordinator helps Anitha install and register
Note: App downloads (18 MB) at FPO office WiFi

API Call: POST /api/v1/farmers/
Payload:
{
  "name": "அனிதா முருகன்",
  "phone": "9442XXXXXX",
  "state": "Tamil Nadu",
  "district": "Pudukkottai",
  "village": "Keeranur",
  "latitude": 10.32,
  "longitude": 78.82,
  "land_size_acres": 1.5,
  "soil_type": "red",
  "irrigation_source": "rainfed",
  "language": "ta"
}

Background Sync (while on WiFi):
- Downloads 10-day weather forecast → cached in SQLite
- Downloads crop recommendations for red soil → cached
- Downloads nearby mandi prices (Pudukkottai, Thanjavur mandis) → cached
- Downloads government scheme info → cached
- Total data downloaded: ~500 KB
```

#### Step 2: Using App Offline (at home/field, no connectivity)

```
Action: Next morning, Anitha opens app at her farm (no internet)
Screen: Shows "ஆஃப்லைன் — cached data" indicator (subtle, non-alarming)

Feature: Crop Recommendation (from cache)
Display: Shows Chickpea, Groundnut, Finger Millet as recommended for red soil, rabi season
Note: All data served from local SQLite, <100ms response

Feature: Weather Forecast (from cache)
Display: Shows 10-day forecast (cached yesterday)
Alert: No weather alerts for her location

Feature: Crop Diary (works fully offline)
Action: Records today's activity via voice input
Voice Input: "இன்று 2 மூட்டை யூரியா போட்டேன்" (Today applied 2 bags urea)
App Parses: crop=current, activity=urea application, category=fertiliser, expense=₹800

API Queue: Entry saved to local SQLite + added to pending_queue
Status: sync_status = 'pending' (will upload when online)
```

#### Step 3: Periodic Sync (brief 4G window)

```
Trigger: Anitha goes to town for shopping (4G available for ~15 minutes)
Background: App detects connectivity change
Auto-sync:
  1. Upload 3 pending diary entries (queued over last 3 days)
  2. Download fresh weather forecast (next 10 days)
  3. Download updated mandi prices
  4. Total data transferred: ~50 KB (efficient delta sync)

All happens automatically in background — Anitha doesn't need to do anything
Notification: "✓ 3 entries synced" (brief toast message)
```

#### Step 4: Government Scheme Discovery

```
Action: Anitha taps "அரசு திட்டங்கள்" (Government Schemes) — from cache
Display: Shows eligible schemes:
  - PM-KISAN: ₹6,000/year — Anitha learns she's eligible
  - Soil Health Card: Free soil testing
  - MNREGA: 100 days guaranteed employment

Action: Anitha notes down the PM-KISAN helpline number to call later
Impact: Anitha was unaware of PM-KISAN; this is her first step to enrollment
```

#### Step 5: Season-End Review

```
Action: After 3 months of diary entries (mostly offline)
API Call: GET /api/v1/diary/4/summary?season=rabi-2024

Response:
{
  "total_expenses": 8500,
  "total_income": 14000,
  "net_profit": 5500,
  "expense_breakdown": {
    "sowing": 1200,
    "fertiliser": 3200,
    "labour": 2500,
    "harvest": 1600
  }
}

Insight: First time Anitha has ever seen her farming profitability in numbers.
She realizes labour is her biggest expense (29%) and considers family labour to
reduce costs next season.
```

### Features Tested
✅ Offline-first operation, ✅ Background sync, ✅ Pending queue for diary, ✅ Cached weather, ✅ Cached prices, ✅ Voice input, ✅ Low-end device (2GB RAM), ✅ 2G connectivity, ✅ Tamil language, ✅ Semi-literate UX

---

## Scenario 5: Rajesh — Multi-Crop Diversified Farmer in Uttar Pradesh

### Farmer Profile

| Detail | Value |
|--------|-------|
| **Name** | Rajesh Kumar |
| **Location** | Village Nangla Tarsu, District Aligarh, Uttar Pradesh |
| **Land** | 6 acres (4 owned + 2 leased) |
| **Soil Type** | Alluvial |
| **Irrigation** | Tubewell (electricity 8 hours/day) |
| **Phone** | Realme C11, Android 10, 4G |
| **Language** | Hindi |
| **Crops** | Grows 3 crops: Wheat (3 acres), Mustard (2 acres), Potato (1 acre) |

### Problem Statement

Rajesh is a diversified farmer managing multiple crops simultaneously. He needs to track expenses and income separately for each crop, get different input schedules, monitor different mandi prices, and deal with different weather sensitivities — all in one app.

### Walkthrough

#### Step 1: Registration and Multi-Crop Setup

```
API Call: POST /api/v1/farmers/
Payload:
{
  "name": "राजेश कुमार",
  "phone": "9412XXXXXX",
  "state": "Uttar Pradesh",
  "district": "Aligarh",
  "land_size_acres": 6.0,
  "soil_type": "alluvial",
  "irrigation_source": "tubewell",
  "language": "hi"
}

Response: 201 Created — farmer_id: 5
```

#### Step 2: Input Guides for Each Crop

```
API Call 1: GET /api/v1/crops/inputs/wheat
Response: 5 stages — land prep, sowing, tillering, flowering, harvest
  - Current stage (Jan): Tillering — apply urea top dressing 30kg/acre

API Call 2: GET /api/v1/crops/inputs/mustard
Response: 4 stages — preparation, sowing, flowering, harvest
  - Current stage (Jan): Flowering — ensure irrigation, watch for aphids

API Call 3: GET /api/v1/inputs/potato
Response: 4 stages — planting, vegetative, tuber formation, harvest
  - Current stage (Jan): Tuber formation — apply potash, watch for late blight

Display: Dashboard showing all 3 crops with current stage and immediate actions
```

#### Step 3: Weather Alert for Frost Risk

```
API Call: GET /api/v1/weather/forecast?latitude=27.88&longitude=78.08&days=10
Response:
  Jan 15: temp_min = 2°C ← FROST RISK

API Call: GET /api/v1/weather/alerts?latitude=27.88&longitude=78.08&crop=potato
Response:
{
  "alerts": [
    {
      "type": "frost",
      "severity": "high",
      "date": "2024-01-15",
      "message": "Frost expected on Jan 15. Minimum temperature: 2°C",
      "message_hi": "15 जनवरी को पाला पड़ने की संभावना। न्यूनतम तापमान: 2°C",
      "recommended_action": "Cover potato beds with straw/mulch. Light irrigation in evening raises soil temperature.",
      "recommended_action_hi": "आलू की क्यारियों को पुआल/मल्च से ढकें। शाम को हल्की सिंचाई करें — मिट्टी का तापमान बढ़ेगा।",
      "crop_affected": "Potato"
    }
  ]
}

Action: Rajesh takes preventive action — irrigates potato field on evening of Jan 14
Outcome: Potato crop saved; neighbouring farmers who didn't irrigate lost 20% yield
```

#### Step 4: Parallel Diary Tracking

```
Diary Entry 1 (Wheat):
POST /api/v1/diary/5
{
  "crop_name": "Wheat",
  "activity": "Urea top dressing - 3 acres × 30kg = 90kg",
  "category": "fertiliser",
  "expense_amount": 540,
  "season": "rabi-2024"
}

Diary Entry 2 (Mustard):
POST /api/v1/diary/5
{
  "crop_name": "Mustard",
  "activity": "Aphid control spray - Imidacloprid on 2 acres",
  "category": "pesticide",
  "expense_amount": 600,
  "season": "rabi-2024"
}

Diary Entry 3 (Potato):
POST /api/v1/diary/5
{
  "crop_name": "Potato",
  "activity": "Emergency frost protection irrigation",
  "category": "irrigation",
  "expense_amount": 300,
  "notes": "Frost alert from app. Irrigated evening Jan 14.",
  "season": "rabi-2024"
}
```

#### Step 5: Staggered Harvest and Selling

```
March: Potato harvested first (90 days)
─────────────────────────────────────
API Call: GET /api/v1/mandi/prices?crop_name=potato&state=Uttar Pradesh
Response: Agra mandi: ₹1,200/quintal, Aligarh: ₹1,050/quintal

API Call: GET /api/v1/mandi/sell-recommendation?crop_name=potato&mandi_name=Agra
Response: { "recommendation": "sell_now", "reasoning": "Price 15% above 30-day average" }

Diary: Sale recorded — 50 quintals × ₹1,200 = ₹60,000 (Agra mandi)

April: Mustard harvested (120 days)
─────────────────────────────────────
API Call: GET /api/v1/mandi/sell-recommendation?crop_name=mustard&mandi_name=Aligarh&msp_price=5650
Response: { "recommendation": "wait", "reasoning": "MSP procurement starts April 10" }

Decision: Rajesh waits 5 days → sells at MSP
Diary: 20 quintals × ₹5,650 = ₹1,13,000

April: Wheat harvested (120 days)
─────────────────────────────────────
API Call: GET /api/v1/mandi/sell-recommendation?crop_name=wheat&mandi_name=Aligarh&msp_price=2275
Response: { "recommendation": "sell_now", "reasoning": "Government procurement active, selling at MSP" }

Diary: 75 quintals × ₹2,275 = ₹1,70,625
```

#### Step 6: Comparative Crop Profitability

```
API Call 1: GET /api/v1/diary/5/summary?season=rabi-2024&crop_name=Wheat
Response:
{
  "total_expenses": 45000,  (3 acres)
  "total_income": 170625,
  "net_profit": 125625,
  "profit_per_acre": 41875
}

API Call 2: GET /api/v1/diary/5/summary?season=rabi-2024&crop_name=Mustard
Response:
{
  "total_expenses": 18000,  (2 acres)
  "total_income": 113000,
  "net_profit": 95000,
  "profit_per_acre": 47500    ← Highest per-acre profit!
}

API Call 3: GET /api/v1/diary/5/summary?season=rabi-2024&crop_name=Potato
Response:
{
  "total_expenses": 35000,  (1 acre)
  "total_income": 60000,
  "net_profit": 25000,
  "profit_per_acre": 25000    ← Lowest, but high absolute revenue
}

Insight: Mustard gave highest profit per acre (₹47,500) with lowest investment.
Rajesh considers increasing mustard area next rabi season from 2 to 3 acres.
```

### Features Tested
✅ Multi-crop management, ✅ Parallel input guides, ✅ Frost weather alert, ✅ Crop-specific alerts, ✅ Multiple diary entries per crop, ✅ Staggered selling, ✅ Multi-mandi comparison, ✅ MSP-aware selling, ✅ Per-crop profitability comparison, ✅ Data-driven crop allocation decisions

---

## Scenario Summary Matrix

| Feature | Scenario 1 (Ramu) | Scenario 2 (Lakshmi) | Scenario 3 (Gurpreet) | Scenario 4 (Anitha) | Scenario 5 (Rajesh) |
|---------|:-:|:-:|:-:|:-:|:-:|
| Registration | ✅ | — | — | ✅ | ✅ |
| Crop Recommendation | ✅ | — | — | ✅ (cached) | — |
| Input Guide | ✅ | — | — | — | ✅ (×3 crops) |
| Weather Forecast | ✅ | ✅ | — | ✅ (cached) | ✅ |
| Weather Alerts | ✅ | — | — | — | ✅ (frost) |
| Disease Detection | — | ✅ | — | — | — |
| Disease Database | — | ✅ | — | — | — |
| Mandi Prices | — | — | ✅ | ✅ (cached) | ✅ |
| Price Trend | — | — | ✅ | — | — |
| Sell Recommendation | — | — | ✅ | — | ✅ (×3 crops) |
| Crop Diary | ✅ | ✅ | ✅ | ✅ (offline) | ✅ (×3 crops) |
| Season Summary | — | ✅ | ✅ | ✅ | ✅ (comparative) |
| Government Schemes | ✅ | — | — | ✅ (cached) | — |
| Offline Mode | — | — | — | ✅ (primary) | — |
| Voice Input | — | — | — | ✅ | — |
| Multi-language | ✅ Hindi | ✅ Hindi | ✅ Hindi | ✅ Tamil | ✅ Hindi |
