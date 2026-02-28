# AI Farmer Assistant — कृषि सहायक

An AI-powered decision-support platform for Indian smallholder farmers. Provides personalized crop recommendations, real-time mandi prices, weather forecasts, disease detection, expense tracking, and government scheme navigation — all in Hindi and 9 other Indian languages, designed to work offline on low-end Android devices.

---

## Why This Exists

India's 120M+ smallholder farmers lose ₹15,000–35,000 per acre annually due to two critical mistakes: **wrong crop selection** and **poor selling timing**. Existing solutions (Plantix, DeHaat, AgroStar) solve isolated problems but none integrate the full farming cycle from seed to sale in an offline-capable, commerce-free app.

AI Farmer Assistant fills this gap.

---

## Features

| Feature | Description | API Endpoint |
|---------|-------------|--------------|
| 🌾 **Crop Advisor** | Recommends top 3 crops based on soil type, season, and land size with profit projections | `GET /api/v1/crops/recommend` |
| 📊 **Mandi Prices** | Daily prices from 7,000+ mandis with multi-market comparison | `GET /api/v1/mandi/prices` |
| 📈 **Price Trends** | 30-day trend analysis (rising/falling/stable) with sell/wait/hold recommendation | `GET /api/v1/mandi/trend` |
| 💰 **Sell Advisor** | Compares current price vs 30-day average vs MSP to recommend optimal selling timing | `GET /api/v1/mandi/sell-recommendation` |
| 🌤️ **Weather Forecast** | 10–16 day forecast via Open-Meteo with crop-specific frost/rain/heat alerts | `GET /api/v1/weather/forecast` |
| 🔬 **Disease Detection** | Upload a crop photo for AI-powered disease identification with treatment steps | `POST /api/v1/pests/detect` |
| 📒 **Crop Diary** | Track expenses and income per crop per season with profitability summaries | `POST /api/v1/diary/{farmer_id}` |
| 🏛️ **Government Schemes** | Automatic eligibility matching for PM-KISAN, PMFBY, KCC, Soil Health Card, eNAM, MNREGA | `GET /api/v1/schemes/` |
| 🌱 **Input Guide** | Stage-by-stage fertiliser, water, and pesticide schedules with costs | `GET /api/v1/crops/inputs/{crop}` |
| 👨‍🌾 **Farmer Profile** | Registration with soil type, location, land size, and language preference | `POST /api/v1/farmers/` |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend Framework** | FastAPI 0.115 | REST API with async support, auto-generated OpenAPI docs |
| **Database (Server)** | PostgreSQL 15 (prod) / SQLite (dev) | Farmer data, diary entries, mandi prices |
| **Database (Mobile)** | SQLite | Offline-first local storage with sync |
| **ORM** | SQLAlchemy 2.0 | Database models and queries |
| **Migrations** | Alembic 1.13 | Schema version control |
| **Validation** | Pydantic 2.9 | Request/response schema validation |
| **HTTP Client** | httpx 0.27 | Async weather API calls |
| **Image Processing** | Pillow 12.1 | Crop disease photo handling |
| **ML (Planned)** | TensorFlow Lite / ONNX | On-device disease detection (EfficientNet-B0) |
| **Auth** | python-jose + passlib | JWT token authentication (configured) |
| **Testing** | pytest + pytest-asyncio | 24 unit tests across all features |
| **Deployment** | AWS Mumbai (ECS Fargate) | Low-latency for Indian users |

---

## Project Structure

```
aifarmer/
├── README.md
├── docs/
│   ├── THINK_ANSWERS.md       # Deep-dive answers to all THINK questions
│   ├── DATA_SOURCES.md        # Complete data source map with APIs and URLs
│   ├── DATABASE_SCHEMA.md     # Database schema, relationships, offline sync design
│   ├── DEPLOYMENT.md          # AWS Mumbai deployment + Play Store submission guide
│   └── FARMER_SCENARIOS.md    # 5 realistic farmer scenario walkthroughs
├── backend/
│   ├── requirements.txt       # Python dependencies
│   ├── alembic.ini            # Database migration config
│   ├── app/
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── config.py          # Environment configuration
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── database.py    # DB connection setup
│   │   │   ├── farmer.py      # Farmer profile model
│   │   │   ├── crop.py        # Crop + CropStage models
│   │   │   ├── diary.py       # Crop diary entry model
│   │   │   └── mandi.py       # Mandi price model
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   │   ├── farmer.py      # Farmer create/update/response
│   │   │   ├── crop.py        # Crop recommendation & input schemas
│   │   │   ├── diary.py       # Diary entry & season summary
│   │   │   ├── mandi.py       # Price, trend, sell recommendation
│   │   │   ├── pest.py        # Disease detection result
│   │   │   ├── scheme.py      # Government scheme response
│   │   │   └── weather.py     # Forecast & weather alert
│   │   ├── routers/           # API endpoint handlers
│   │   │   ├── farmers.py     # CRUD + phone lookup
│   │   │   ├── crops.py       # Recommendation + input guide
│   │   │   ├── diary.py       # Diary CRUD + season summary
│   │   │   ├── mandi.py       # Prices + trends + sell advice
│   │   │   ├── pests.py       # Disease detection + database
│   │   │   ├── inputs.py      # Alternative input guide endpoint
│   │   │   ├── schemes.py     # Government scheme eligibility
│   │   │   └── weather.py     # Forecast + crop-specific alerts
│   │   ├── services/          # Business logic layer
│   │   │   ├── crop_service.py    # Scoring algorithm, input schedules
│   │   │   ├── diary_service.py   # CRUD + profitability calculations
│   │   │   ├── mandi_service.py   # Price analysis + sell recommendation
│   │   │   ├── pest_service.py    # Disease DB + detection placeholder
│   │   │   ├── scheme_service.py  # Scheme data + eligibility matching
│   │   │   └── weather_service.py # Open-Meteo integration + alerts
│   │   └── ml/
│   │       └── disease_detection.py  # ML model placeholder (EfficientNet-B0)
│   └── tests/                 # Test suite (24 tests)
│       ├── conftest.py        # Test DB setup + fixtures
│       ├── test_farmers.py    # 6 farmer CRUD tests
│       ├── test_crops.py      # 4 crop recommendation tests
│       ├── test_diary.py      # 4 diary + summary tests
│       ├── test_mandi.py      # 3 mandi price tests
│       ├── test_pests.py      # 4 disease detection tests
│       ├── test_schemes.py    # 2 scheme tests
│       └── test_health.py     # 1 health check test
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/<org>/aifarmer.git
cd aifarmer/backend

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000

# The API is now live at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Run Tests

```bash
cd backend
pytest tests/ -v
```

### Health Check

```bash
curl http://localhost:8000/health
# {"status":"healthy","app":"AI Farmer Assistant"}
```

---

## API Overview

All endpoints are prefixed with `/api/v1/`. Full interactive documentation is available at `/docs` (Swagger UI) when the server is running.

### Farmer Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/farmers/` | Register a new farmer |
| `GET` | `/api/v1/farmers/{id}` | Get farmer profile |
| `PUT` | `/api/v1/farmers/{id}` | Update farmer profile |
| `GET` | `/api/v1/farmers/phone/{phone}` | Lookup farmer by phone |

### Crop Advisory

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/crops/recommend` | Get top 3 crop recommendations |
| `GET` | `/api/v1/crops/inputs/{crop}` | Stage-wise input guide |
| `GET` | `/api/v1/inputs/{crop}` | Alternative input guide endpoint |

### Market Intelligence

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/mandi/prices` | Latest mandi prices by crop/state |
| `GET` | `/api/v1/mandi/trend` | 30-day price trend analysis |
| `GET` | `/api/v1/mandi/sell-recommendation` | Sell/wait/hold recommendation |

### Weather

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/weather/forecast` | 10–16 day weather forecast |
| `GET` | `/api/v1/weather/alerts` | Crop-specific weather alerts |

### Disease Detection

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/pests/detect` | Upload image for disease diagnosis |
| `GET` | `/api/v1/pests/diseases` | List all known diseases |
| `GET` | `/api/v1/pests/diseases/{key}` | Get disease details and treatment |

### Crop Diary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/diary/{farmer_id}` | Add diary entry |
| `GET` | `/api/v1/diary/{farmer_id}` | List diary entries (filterable) |
| `GET` | `/api/v1/diary/{farmer_id}/summary` | Season profitability summary |

### Government Schemes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/schemes/` | Get eligible government schemes |

---

## Documentation

| Document | Description |
|----------|-------------|
| [THINK Answers](docs/THINK_ANSWERS.md) | Deep-dive analysis of farming cycles, data needs, government APIs, phone constraints, competition, and the trust problem |
| [Data Sources](docs/DATA_SOURCES.md) | Complete map of every API and data source — Open-Meteo, Agmarknet, eNAM, MSP, Soil Health Card, PlantVillage |
| [Database Schema](docs/DATABASE_SCHEMA.md) | All tables, relationships, field definitions, and the offline sync design with SQLite |
| [Deployment Guide](docs/DEPLOYMENT.md) | Step-by-step AWS Mumbai deployment (ECS Fargate + RDS) and Google Play Store submission |
| [Farmer Scenarios](docs/FARMER_SCENARIOS.md) | 5 realistic end-to-end farmer walkthroughs testing every feature |

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Offline-first architecture** | 60%+ of target users have unreliable 2G/4G connectivity |
| **SQLite local database** | All user data works without internet; sync when connected |
| **Voice-first input** | 30–40% of rural smartphone users are semi-literate |
| **Hindi + 9 languages** | Reaching farmers in their native language builds trust |
| **No commerce/marketplace** | Unbiased recommendations — we don't sell inputs |
| **MSP-aware recommendations** | Government price guarantees reduce farmer risk |
| **<25 MB app size** | Target devices have 16–32 GB storage, often 50%+ used |
| **Open-Meteo over IMD** | Free, reliable API vs no public API from IMD |
| **FastAPI backend** | Async support, auto-docs, Python ML ecosystem compatibility |

---

## License

This project is part of an academic/hackathon submission. See individual file headers for attribution.