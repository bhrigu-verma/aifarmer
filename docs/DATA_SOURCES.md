# Data Sources — AI Farmer Assistant

Complete map of every data source used or planned for the AI Farmer Assistant platform, including APIs, scraping targets, static datasets, and user-generated data.

---

## Overview

```
Data Pipeline Architecture:

External Sources          Ingestion Layer         Internal Storage        App Layer
┌─────────────────┐      ┌──────────────┐       ┌──────────────┐      ┌───────────┐
│ Open-Meteo API  │─────→│ Async HTTP   │──────→│ PostgreSQL   │─────→│ REST API  │
│ Agmarknet       │─────→│ Web Scraper  │──────→│ (Server DB)  │─────→│ (FastAPI) │
│ eNAM Dashboard  │─────→│ Scheduled    │──────→│              │      └───────────┘
│ Static Datasets │─────→│ Jobs         │       │              │           │
│ User Input      │      └──────────────┘       └──────────────┘           │
│                 │                                                         ▼
│                 │                                                  ┌───────────┐
│                 │                                                  │ SQLite    │
│                 │                                                  │ (Offline) │
│                 │                                                  └───────────┘
└─────────────────┘
```

---

## 1. Weather Data

### Primary: Open-Meteo API

| Field | Details |
|-------|---------|
| **Provider** | Open-Meteo (open-source weather API) |
| **URL** | `https://api.open-meteo.com/v1/forecast` |
| **Access** | Free, no API key required (non-commercial: 10,000 requests/day) |
| **Protocol** | HTTPS REST, JSON response |
| **Coverage** | Global, 1km resolution |
| **Forecast Range** | Up to 16 days |
| **Update Frequency** | Every 1–3 hours |
| **Latency** | ~200ms from India |

#### Parameters We Use

```http
GET https://api.open-meteo.com/v1/forecast
  ?latitude=20.5937
  &longitude=78.9629
  &daily=temperature_2m_max,temperature_2m_min,precipitation_sum,
         relative_humidity_2m_mean,wind_speed_10m_max,weathercode
  &timezone=Asia/Kolkata
  &forecast_days=10
```

#### Response Fields Mapped

| API Field | Our Field | Unit | Usage |
|-----------|-----------|------|-------|
| `temperature_2m_max` | `temp_max` | °C | Heat wave alerts (>42°C) |
| `temperature_2m_min` | `temp_min` | °C | Frost alerts (<4°C) |
| `precipitation_sum` | `precipitation` | mm | Heavy rain alerts (>50mm) |
| `relative_humidity_2m_mean` | `humidity` | % | Disease risk assessment |
| `wind_speed_10m_max` | `wind_speed` | km/h | Spray timing advisory |
| `weathercode` | `description` | WMO code | Human-readable forecast |

#### WMO Weather Code Mapping

| Code | Description | Farming Impact |
|------|-------------|----------------|
| 0 | Clear sky | Good for spraying, harvesting |
| 1–3 | Partly cloudy to overcast | Normal operations |
| 45, 48 | Fog | Delay spraying |
| 51–55 | Drizzle | Delay spraying, check drainage |
| 61–65 | Rain (slight to heavy) | Stop field operations, check bunds |
| 71–77 | Snow/sleet | Protect standing crop |
| 80–82 | Rain showers | Plan irrigation accordingly |
| 95, 96, 99 | Thunderstorm (with hail) | Harvest warning, PMFBY claim trigger |

### Secondary: IMD (India Meteorological Department)

| Field | Details |
|-------|---------|
| **Provider** | IMD, Government of India |
| **URL** | `https://mausam.imd.gov.in` |
| **Access** | No public API; web portal only |
| **Data Available** | District-wise 5-day forecast, rainfall data, cyclone warnings |
| **Access Method** | Web scraping (fragile, not recommended for production) |
| **Status** | 🔄 Future integration for extreme weather alerts |

---

## 2. Market Price Data

### Primary: Agmarknet

| Field | Details |
|-------|---------|
| **Provider** | Directorate of Marketing & Inspection, Govt. of India |
| **URL** | `https://agmarknet.gov.in` |
| **Access** | Public website, no API; requires form POST scraping |
| **Coverage** | ~7,000 regulated mandis across India |
| **Commodities** | 300+ commodities including all major crops |
| **Update Frequency** | Daily (prices from previous trading day) |
| **Data Lag** | 1–2 days |

#### Data Fields Available

| Field | Description | Example |
|-------|-------------|---------|
| State | State name | Maharashtra |
| District | District name | Nagpur |
| Market | Mandi name | Nagpur (Kalamna) |
| Commodity | Crop name | Soybean |
| Variety | Crop variety | Yellow |
| Grade | Quality grade | FAQ |
| Min Price | Lowest trade price | ₹4,200/quintal |
| Max Price | Highest trade price | ₹4,800/quintal |
| Modal Price | Most traded price | ₹4,500/quintal |
| Price Date | Date of trading | 2024-11-15 |

#### Scraping Strategy

```python
# Conceptual scraping approach (Agmarknet)
# POST to: https://agmarknet.gov.in/SearchCmmMkt.aspx

form_data = {
    "Ession_commodity": "24",     # Commodity code (Wheat=24)
    "Ession_state": "MH",         # State code
    "Session_district": "0",      # All districts
    "Session_market": "0",        # All markets
    "DateFrom": "15-Nov-2024",
    "DateTo": "15-Nov-2024",
}

# Schedule: Daily at 06:00 IST (after previous day data is uploaded)
# Normalize: Strip whitespace, standardize commodity names, convert to float
# Store: mandi_prices table with deduplication on (crop, mandi, date)
```

### Secondary: eNAM (National Agriculture Market)

| Field | Details |
|-------|---------|
| **Provider** | Small Farmers' Agribusiness Consortium (SFAC), Govt. of India |
| **URL** | `https://enam.gov.in/web/dashboard/trade-data` |
| **Access** | Dashboard is public; API requires partner registration |
| **Coverage** | 1,000+ mandis integrated with eNAM platform |
| **Update Frequency** | Near real-time (during trading hours) |
| **Status** | 🔄 API partnership application planned |

#### eNAM Data Fields

| Field | Description |
|-------|-------------|
| Commodity | Crop name |
| Lot ID | Trading lot identifier |
| Quantity | Quintal |
| Min/Max/Modal Price | ₹/quintal |
| Mandi | Market name |
| State | State |
| Timestamp | Trade timestamp |

---

## 3. Crop & Agricultural Data

### MSP (Minimum Support Price)

| Field | Details |
|-------|---------|
| **Provider** | Commission for Agricultural Costs & Prices (CACP), DAC&FW |
| **URL** | `https://agricoop.nic.in`, `https://cacp.dacnet.nic.in` |
| **Access** | Published annually as government gazette (PDF) |
| **Coverage** | 23 crops (14 kharif + 6 rabi + 2 commercial + 1 sugarcane FRP) |
| **Update Frequency** | Annual (announced before sowing season) |
| **Format** | Static data — manually updated in application |

#### Current MSP Rates (Rabi 2024-25)

| Crop | MSP (₹/quintal) | Season |
|------|-----------------|--------|
| Wheat | 2,275 | Rabi |
| Barley | 1,850 | Rabi |
| Gram (Chana) | 5,440 | Rabi |
| Masur (Lentil) | 6,425 | Rabi |
| Mustard/Rapeseed | 5,650 | Rabi |
| Safflower | 5,800 | Rabi |

#### Current MSP Rates (Kharif 2024)

| Crop | MSP (₹/quintal) | Season |
|------|-----------------|--------|
| Paddy (Common) | 2,300 | Kharif |
| Jowar (Hybrid) | 3,371 | Kharif |
| Bajra | 2,500 | Kharif |
| Maize | 2,225 | Kharif |
| Cotton (Medium Staple) | 7,121 | Kharif |
| Soybean (Yellow) | 4,892 | Kharif |
| Groundnut | 6,377 | Kharif |

### Crop Database (Internal)

Hardcoded in `backend/app/services/crop_service.py`:

| Crop | Season | Duration (days) | Avg Cost/Acre | Avg Revenue/Acre | Suitable Soils |
|------|--------|----------------|---------------|-------------------|----------------|
| Wheat | Rabi | 120 | ₹12,000 | ₹25,000 | Alluvial, Loamy, Clay |
| Rice (Paddy) | Kharif | 120 | ₹15,000 | ₹28,000 | Alluvial, Clay, Loamy |
| Cotton | Kharif | 180 | ₹20,000 | ₹35,000 | Black, Alluvial |
| Soybean | Kharif | 100 | ₹10,000 | ₹22,000 | Black, Loamy |
| Mustard | Rabi | 120 | ₹8,000 | ₹20,000 | Sandy, Loamy, Alluvial |
| Sugarcane | Kharif | 360 | ₹35,000 | ₹70,000 | Alluvial, Loamy, Black |
| Chickpea | Rabi | 100 | ₹8,000 | ₹22,000 | Black, Loamy, Red |
| Tomato | Kharif | 75 | ₹25,000 | ₹50,000 | Loamy, Red, Alluvial |
| Potato | Rabi | 90 | ₹20,000 | ₹40,000 | Sandy, Loamy, Alluvial |
| Maize | Kharif | 100 | ₹10,000 | ₹20,000 | Loamy, Alluvial, Red |

---

## 4. Soil Data

### Soil Health Card Portal

| Field | Details |
|-------|---------|
| **Provider** | Department of Agriculture & Farmers Welfare |
| **URL** | `https://soilhealth.dac.gov.in` |
| **Access** | Public lookup by farmer registration or sample ID |
| **Data Fields** | pH, organic carbon, N/P/K levels, micronutrients (Zn, Fe, Cu, Mn, B) |
| **Coverage** | 23+ crore soil health cards issued |
| **Limitation** | No bulk API; per-card lookup only; many cards are 2+ years old |

### Our Approach: User Self-Report

During farmer registration, we collect soil type as an enum:

| Soil Type | Typical Regions | Key Crops |
|-----------|----------------|-----------|
| **Alluvial** | Indo-Gangetic plains (UP, Bihar, Punjab, Haryana) | Wheat, rice, sugarcane |
| **Black (Regur)** | Deccan Plateau (Maharashtra, MP, Gujarat) | Cotton, soybean, wheat |
| **Red** | Tamil Nadu, Karnataka, Andhra Pradesh, Jharkhand | Millets, groundnut, pulses |
| **Laterite** | Kerala, Goa, parts of Karnataka | Cashew, rubber, tea |
| **Sandy** | Rajasthan, parts of Gujarat, Haryana | Mustard, bajra, guar |
| **Clay** | Coastal areas, river deltas | Rice, jute |
| **Loamy** | Mixed regions | Most crops (ideal) |

---

## 5. Disease Detection Data

### Training Dataset: PlantVillage

| Field | Details |
|-------|---------|
| **Provider** | Penn State University (open-source) |
| **URL** | `https://plantvillage.psu.edu` / Kaggle mirror |
| **Images** | 54,306 images across 38 classes (14 crop species) |
| **Format** | JPEG, ~256x256px |
| **License** | CC-BY-SA (open for research and commercial use) |
| **Coverage** | Tomato (10 diseases), Potato (3), Grape (4), Apple (4), Corn (4), etc. |
| **Limitation** | Lab-controlled images — less noisy than real field photos |

### Internal Disease Database

Pre-loaded in `backend/app/services/pest_service.py`:

| Disease Key | Crop(s) | Severity | Confidence |
|-------------|---------|----------|------------|
| `leaf_blight` | Rice, Wheat | Moderate | — |
| `powdery_mildew` | Wheat, Vegetables | Mild | — |
| `late_blight` | Potato, Tomato | Severe | — |
| `bollworm` | Cotton | Severe | — |
| `rust` | Wheat | Moderate | — |

Each disease record includes:
- Name (English + Hindi)
- Description
- Treatment steps (English + Hindi)
- Recommended products (with dosage)
- Severity classification
- Prevention tips

### Planned Data Collection

| Source | Method | Target |
|--------|--------|--------|
| User uploads | Validated by agronomist panel | 500+ images/disease for Indian crops |
| ICAR publications | Manual curation from research papers | Disease-region mapping |
| KVK (Krishi Vigyan Kendra) | Partnership for field-validated images | 10 priority crops |

---

## 6. Government Schemes Data

### Static Database (Internal)

Currently hardcoded in `backend/app/services/scheme_service.py`:

| Scheme | Type | Key Benefit | Eligibility |
|--------|------|-------------|-------------|
| **PM-KISAN** | Direct Benefit Transfer | ₹6,000/year in 3 installments | All farmers with cultivable land |
| **PM Fasal Bima Yojana** | Crop Insurance | Premium: 2% kharif, 1.5% rabi | All farmers (mandatory for loan holders) |
| **Kisan Credit Card** | Credit | Up to ₹3L at 4% interest | All farmers with land records |
| **Soil Health Card** | Advisory | Free soil testing + recommendations | All farmers |
| **eNAM** | Market Access | Direct mandi trading via app | Farmers in eNAM-integrated mandis |
| **MNREGA** | Employment | 100 days guaranteed work at ₹267/day | Rural households |

### Data Sources for Schemes

| Source | URL | Data Available |
|--------|-----|----------------|
| PM-KISAN Portal | `https://pmkisan.gov.in` | Beneficiary status, payment history |
| PMFBY Portal | `https://pmfby.gov.in` | Premium calculator, claim status |
| KCC Portal | `https://eseva.csccloud.in/KCC` | Application status |
| Soil Health Card | `https://soilhealth.dac.gov.in` | Test results, recommendations |
| eNAM | `https://enam.gov.in` | Market list, trade data |
| MNREGA | `https://nrega.nic.in` | Job card status, wage payments |

---

## 7. User-Generated Data

### Farmer Profile Data

Collected during registration via `POST /api/v1/farmers/`:

| Field | Type | Required | Source |
|-------|------|----------|--------|
| `name` | String | Yes | User input |
| `phone` | String (10 digits) | Yes | User input (unique identifier) |
| `state` | String | Yes | User selection |
| `district` | String | Yes | User selection |
| `village` | String | No | User input |
| `latitude` | Float | No | GPS (auto-detected) |
| `longitude` | Float | No | GPS (auto-detected) |
| `land_size_acres` | Float | Yes | User input |
| `soil_type` | Enum | Yes | User selection |
| `irrigation_source` | String | No | User input |
| `language` | Enum | Yes | User selection (default: Hindi) |

### Crop Diary Data

Collected via `POST /api/v1/diary/{farmer_id}`:

| Field | Type | Required | Examples |
|-------|------|----------|----------|
| `entry_date` | Date | No (default: today) | 2024-11-15 |
| `crop_name` | String | Yes | Wheat, Rice |
| `activity` | String | Yes | "DAP 2 bags applied" |
| `category` | Enum | Yes | sowing/irrigation/fertiliser/pesticide/labour/harvest/sale |
| `expense_amount` | Float | No | 2400.00 |
| `income_amount` | Float | No | 0.00 |
| `notes` | String | No | "Used 50kg DAP per acre" |
| `season` | String | No | "rabi-2024" |

---

## 8. Data Freshness & Sync Strategy

| Data Type | Server Update | Client Cache TTL | Offline Available |
|-----------|---------------|-------------------|-------------------|
| Weather forecast | Every 3 hours | 6 hours | ✅ Last sync cached |
| Mandi prices | Daily 06:00 IST | 24 hours | ✅ Last 7 days cached |
| Crop database | On app update | 30 days | ✅ Bundled with app |
| Disease database | On app update | 30 days | ✅ Bundled with app |
| Scheme information | Monthly | 30 days | ✅ Bundled with app |
| MSP rates | Annually | 365 days | ✅ Bundled with app |
| Farmer profile | On change | Permanent | ✅ Local SQLite |
| Diary entries | On change | Permanent | ✅ Local SQLite |

---

## 9. Data Quality & Validation

### Known Issues

| Source | Issue | Mitigation |
|--------|-------|------------|
| Agmarknet | Inconsistent commodity naming (e.g., "Wheat" vs "WHEAT" vs "Gehu") | Normalization dictionary |
| Agmarknet | Missing data for small mandis | Mark data completeness; show "last updated" |
| Open-Meteo | 14-16 day forecast less accurate | Show confidence band; only alert on high-confidence events |
| User soil type | Self-reported, may be inaccurate | Cross-validate against regional soil maps |
| Disease detection | PlantVillage images differ from field conditions | Collect and validate Indian field images |

### Data Validation Rules

```python
# Price validation
assert min_price > 0
assert min_price <= modal_price <= max_price
assert max_price < min_price * 10  # Reject >10x spread (likely error)

# Weather validation  
assert -10 <= temp_min <= 55  # Valid temperature range for India
assert 0 <= precipitation <= 500  # Max daily rainfall
assert 0 <= humidity <= 100

# Phone validation
assert re.match(r'^[6-9]\d{9}$', phone)  # Indian mobile numbers start with 6-9

# Land size validation
assert 0 < land_size_acres <= 1000  # Reasonable range
```
