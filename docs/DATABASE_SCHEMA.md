# Database Schema — AI Farmer Assistant

Complete documentation of the database schema, table relationships, and the offline sync design with SQLite.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     Server (PostgreSQL)                       │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌───────────┐ │
│  │ farmers  │  │  crops   │  │crop_stages │  │mandi_prices│ │
│  └────┬─────┘  └──────────┘  └────────────┘  └───────────┘ │
│       │                                                      │
│       │ 1:N                                                  │
│       ▼                                                      │
│  ┌──────────────┐                                            │
│  │ diary_entries │                                            │
│  └──────────────┘                                            │
└──────────────────────────────────────────────────────────────┘
                         │
                    Sync Layer
                         │
┌──────────────────────────────────────────────────────────────┐
│                   Mobile App (SQLite)                         │
│                                                              │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌─────────┐ │
│  │ farmer   │  │ diary_entries │  │  cache   │  │sync_log │ │
│  │ (local)  │  │   (local)    │  │(weather, │  │         │ │
│  │          │  │              │  │ prices)  │  │         │ │
│  └──────────┘  └──────────────┘  └──────────┘  └─────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## Server Database Tables

### 1. `farmers` Table

Stores registered farmer profiles.

```sql
CREATE TABLE farmers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(100)    NOT NULL,
    phone           VARCHAR(15)     NOT NULL UNIQUE,
    state           VARCHAR(50)     NOT NULL,
    district        VARCHAR(50)     NOT NULL,
    village         VARCHAR(100),
    latitude        FLOAT,
    longitude       FLOAT,
    land_size_acres FLOAT           NOT NULL,
    soil_type       VARCHAR(20)     NOT NULL,  -- ENUM: alluvial|black|red|laterite|sandy|clay|loamy
    irrigation_source VARCHAR(50),
    language        VARCHAR(5)      DEFAULT 'hi',  -- ENUM: hi|en|mr|ta|te|kn|bn|gu|pa|ml
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE UNIQUE INDEX ix_farmers_phone ON farmers(phone);
CREATE INDEX ix_farmers_state_district ON farmers(state, district);
```

#### Field Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique farmer identifier |
| `name` | String(100) | NOT NULL | Farmer's full name |
| `phone` | String(15) | NOT NULL, UNIQUE | 10-digit Indian mobile number (validated: `^[6-9]\d{9}$`) |
| `state` | String(50) | NOT NULL | Indian state name |
| `district` | String(50) | NOT NULL | District within state |
| `village` | String(100) | Optional | Village name |
| `latitude` | Float | Optional | GPS latitude (auto-detected or manual) |
| `longitude` | Float | Optional | GPS longitude |
| `land_size_acres` | Float | NOT NULL, > 0 | Total cultivable land in acres |
| `soil_type` | Enum | NOT NULL | One of: alluvial, black, red, laterite, sandy, clay, loamy |
| `irrigation_source` | String(50) | Optional | e.g., borewell, canal, rainfed, drip |
| `language` | Enum | Default: 'hi' | Preferred language (10 Indian languages supported) |
| `created_at` | DateTime | Auto | Registration timestamp |
| `updated_at` | DateTime | Auto | Last profile update timestamp |

#### Supported Languages

| Code | Language | Script |
|------|----------|--------|
| `hi` | Hindi | देवनागरी |
| `en` | English | Latin |
| `mr` | Marathi | देवनागरी |
| `ta` | Tamil | தமிழ் |
| `te` | Telugu | తెలుగు |
| `kn` | Kannada | ಕನ್ನಡ |
| `bn` | Bengali | বাংলা |
| `gu` | Gujarati | ગુજરાતી |
| `pa` | Punjabi | ਗੁਰਮੁਖੀ |
| `ml` | Malayalam | മലയാളം |

---

### 2. `crops` Table

Master crop reference data with agronomy and economics.

```sql
CREATE TABLE crops (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    name                    VARCHAR(100) NOT NULL UNIQUE,
    name_hi                 VARCHAR(100),           -- Hindi name
    season                  VARCHAR(20)  NOT NULL,   -- kharif|rabi|zaid
    duration_days           INTEGER,
    water_requirement       VARCHAR(20),             -- low|medium|high
    suitable_soil_types     JSON,                    -- ["alluvial", "loamy"]
    min_temperature         FLOAT,
    max_temperature         FLOAT,
    avg_yield_per_acre      FLOAT,                   -- quintals
    avg_cost_per_acre       FLOAT,                   -- INR
    avg_revenue_per_acre    FLOAT,                   -- INR
    is_msp_crop             BOOLEAN     DEFAULT FALSE,
    msp_price_per_quintal   FLOAT
);

CREATE UNIQUE INDEX ix_crops_name ON crops(name);
CREATE INDEX ix_crops_season ON crops(season);
```

#### Field Details

| Column | Type | Description |
|--------|------|-------------|
| `name` | String(100) | English crop name (unique key) |
| `name_hi` | String(100) | Hindi crop name (e.g., गेहूं for Wheat) |
| `season` | Enum | Growing season: kharif (monsoon), rabi (winter), zaid (summer) |
| `duration_days` | Integer | Crop cycle length in days |
| `water_requirement` | Enum | Water intensity: low, medium, high |
| `suitable_soil_types` | JSON Array | List of compatible soil types |
| `min_temperature` | Float | Minimum tolerable temperature (°C) |
| `max_temperature` | Float | Maximum tolerable temperature (°C) |
| `avg_yield_per_acre` | Float | Expected yield in quintals per acre |
| `avg_cost_per_acre` | Float | Total input cost in INR per acre |
| `avg_revenue_per_acre` | Float | Expected revenue in INR per acre |
| `is_msp_crop` | Boolean | Whether MSP is guaranteed by government |
| `msp_price_per_quintal` | Float | Current MSP rate in INR/quintal |

---

### 3. `crop_stages` Table

Stage-wise crop management guidance (e.g., sowing, vegetative, flowering, harvest).

```sql
CREATE TABLE crop_stages (
    id                              INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_id                         INTEGER NOT NULL REFERENCES crops(id),
    stage_name                      VARCHAR(100) NOT NULL,
    stage_order                     INTEGER NOT NULL,
    duration_days                   INTEGER,
    fertiliser_type                 VARCHAR(100),
    fertiliser_quantity_kg_per_acre FLOAT,
    water_frequency_days            INTEGER,
    water_quantity_litres_per_acre   FLOAT,
    pesticide_name                  VARCHAR(100),
    pesticide_quantity_ml_per_acre  FLOAT,
    care_instructions               TEXT,        -- English
    care_instructions_hi            TEXT         -- Hindi
);

CREATE INDEX ix_crop_stages_crop_id ON crop_stages(crop_id);
```

#### Relationship

- **Parent**: `crops` (via `crop_id` foreign key)
- **Cardinality**: One crop → many stages (typically 4-6 stages per crop)
- **Ordering**: `stage_order` defines the sequence (1 = first stage)

---

### 4. `diary_entries` Table

Farmer's crop diary for expense/income tracking.

```sql
CREATE TABLE diary_entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id       INTEGER     NOT NULL REFERENCES farmers(id),
    entry_date      DATE        DEFAULT CURRENT_DATE,
    crop_name       VARCHAR(100) NOT NULL,
    activity        VARCHAR(200) NOT NULL,
    category        VARCHAR(20)  NOT NULL,  -- sowing|irrigation|fertiliser|pesticide|labour|harvest|sale
    expense_amount  FLOAT       DEFAULT 0.0,
    income_amount   FLOAT       DEFAULT 0.0,
    notes           TEXT,
    season          VARCHAR(20),            -- e.g., "kharif-2024", "rabi-2024"
    created_at      DATETIME    DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_diary_farmer_id ON diary_entries(farmer_id);
CREATE INDEX ix_diary_season ON diary_entries(season);
CREATE INDEX ix_diary_crop ON diary_entries(crop_name);
CREATE INDEX ix_diary_date ON diary_entries(entry_date);
```

#### Field Details

| Column | Type | Description |
|--------|------|-------------|
| `farmer_id` | Integer | FK → farmers.id |
| `entry_date` | Date | Date of activity (defaults to today) |
| `crop_name` | String(100) | Which crop this entry is for |
| `activity` | String(200) | Description of activity (e.g., "Applied 2 bags DAP") |
| `category` | Enum | One of: sowing, irrigation, fertiliser, pesticide, labour, harvest, sale |
| `expense_amount` | Float | Cost incurred (₹), default 0.0, must be ≥ 0 |
| `income_amount` | Float | Revenue earned (₹), default 0.0, must be ≥ 0 |
| `notes` | Text | Free-text notes |
| `season` | String(20) | Season identifier (e.g., "rabi-2024") |

#### Aggregation Queries

```sql
-- Season summary for a farmer
SELECT
    SUM(expense_amount)  AS total_expenses,
    SUM(income_amount)   AS total_income,
    SUM(income_amount) - SUM(expense_amount) AS net_profit,
    category,
    SUM(expense_amount) AS category_expense
FROM diary_entries
WHERE farmer_id = ? AND season = ?
GROUP BY category;
```

---

### 5. `mandi_prices` Table

Daily market prices from agricultural mandis (wholesale markets).

```sql
CREATE TABLE mandi_prices (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_name   VARCHAR(100) NOT NULL,
    mandi_name  VARCHAR(100) NOT NULL,
    state       VARCHAR(50)  NOT NULL,
    district    VARCHAR(50),
    min_price   FLOAT        NOT NULL,
    max_price   FLOAT        NOT NULL,
    modal_price FLOAT        NOT NULL,
    price_unit  VARCHAR(20)  DEFAULT 'INR/quintal',
    price_date  DATE         DEFAULT CURRENT_DATE,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_mandi_crop ON mandi_prices(crop_name);
CREATE INDEX ix_mandi_date ON mandi_prices(price_date);
CREATE INDEX ix_mandi_state ON mandi_prices(state);
CREATE INDEX ix_mandi_name ON mandi_prices(mandi_name);
```

#### Price Trend Calculation Logic

```python
# From mandi_service.py
def calculate_trend(prices: List[MandiPrice], days: int = 30):
    """
    Split prices into first-half and second-half.
    Compare averages:
    - Rising:  second_half_avg > first_half_avg * 1.05  (+5%)
    - Falling: second_half_avg < first_half_avg * 0.95  (-5%)
    - Stable:  within ±5%
    """
```

#### Sell Recommendation Logic

```python
def get_sell_recommendation(current_price, avg_30d, msp_price):
    """
    - SELL_NOW:  current_price >= avg_30d * 1.10  (10% above average)
    - WAIT:     current_price <= avg_30d * 0.90  (10% below average)
    - HOLD:     otherwise (near average, wait for better opportunity)
    
    Additional: Always compare against MSP as price floor.
    """
```

---

## Entity Relationship Diagram

```
┌──────────────────┐          ┌──────────────────┐
│     farmers      │          │      crops       │
├──────────────────┤          ├──────────────────┤
│ id (PK)          │          │ id (PK)          │
│ name             │          │ name (UNIQUE)    │
│ phone (UNIQUE)   │          │ name_hi          │
│ state            │          │ season           │
│ district         │          │ duration_days    │
│ village          │          │ water_requirement│
│ latitude         │          │ suitable_soils   │
│ longitude        │          │ min/max_temp     │
│ land_size_acres  │          │ yield/cost/rev   │
│ soil_type        │          │ is_msp_crop      │
│ irrigation_source│          │ msp_price        │
│ language         │          └────────┬─────────┘
│ created_at       │                   │
│ updated_at       │                   │ 1:N
└────────┬─────────┘                   │
         │                   ┌─────────▼─────────┐
         │ 1:N               │   crop_stages     │
         │                   ├───────────────────┤
         ▼                   │ id (PK)           │
┌──────────────────┐         │ crop_id (FK)      │
│  diary_entries   │         │ stage_name        │
├──────────────────┤         │ stage_order       │
│ id (PK)          │         │ duration_days     │
│ farmer_id (FK)   │         │ fertiliser_*      │
│ entry_date       │         │ water_*           │
│ crop_name        │         │ pesticide_*       │
│ activity         │         │ care_instructions │
│ category         │         └───────────────────┘
│ expense_amount   │
│ income_amount    │         ┌───────────────────┐
│ notes            │         │   mandi_prices    │
│ season           │         ├───────────────────┤
│ created_at       │         │ id (PK)           │
└──────────────────┘         │ crop_name         │
                             │ mandi_name        │
                             │ state, district   │
                             │ min/max/modal     │
                             │ price_unit        │
                             │ price_date        │
                             │ created_at        │
                             └───────────────────┘
```

### Relationships Summary

| From | To | Type | FK Column | Description |
|------|----|------|-----------|-------------|
| `diary_entries` | `farmers` | N:1 | `farmer_id` | Each diary entry belongs to one farmer |
| `crop_stages` | `crops` | N:1 | `crop_id` | Each stage belongs to one crop |
| `diary_entries.crop_name` | `crops.name` | Logical (not FK) | — | Linked by crop name string (flexible) |
| `mandi_prices.crop_name` | `crops.name` | Logical (not FK) | — | Linked by crop name string |

> **Design Note**: `diary_entries.crop_name` and `mandi_prices.crop_name` use string matching rather than foreign keys intentionally — this allows farmers to enter custom crop names and mandi data to include crops not in our master database.

---

## Offline Sync Design with SQLite

### Architecture

The app uses a **local-first** architecture where the mobile device maintains a SQLite database as the primary data store, syncing with the server PostgreSQL database when connectivity is available.

```
Mobile App (SQLite)                    Server (PostgreSQL)
┌─────────────────┐                   ┌─────────────────┐
│ farmer_profile  │◄────────────────►│ farmers          │
│ diary_entries   │◄────────────────►│ diary_entries    │
│ weather_cache   │◄────────────────│ (Open-Meteo API) │
│ price_cache     │◄────────────────│ mandi_prices     │
│ crop_cache      │◄────────────────│ crops            │
│ scheme_cache    │◄────────────────│ (static data)    │
│ sync_metadata   │                  │                  │
│ pending_queue   │─────────────────►│ (processing)     │
└─────────────────┘                   └─────────────────┘
        │
   ◄──Bidirectional sync──►
   ◄──Server-to-client cache──
   ──Client-to-server queue──►
```

### SQLite Schema (Mobile)

#### `farmer_profile` (Single Row)
```sql
CREATE TABLE farmer_profile (
    id              INTEGER PRIMARY KEY,
    server_id       INTEGER,            -- Matches farmers.id on server
    name            TEXT NOT NULL,
    phone           TEXT NOT NULL,
    state           TEXT NOT NULL,
    district        TEXT NOT NULL,
    village         TEXT,
    latitude        REAL,
    longitude       REAL,
    land_size_acres REAL NOT NULL,
    soil_type       TEXT NOT NULL,
    irrigation_source TEXT,
    language        TEXT DEFAULT 'hi',
    last_synced_at  TEXT                -- ISO 8601 timestamp
);
```

#### `diary_entries` (Local + Sync)
```sql
CREATE TABLE diary_entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id       INTEGER,            -- NULL until synced
    farmer_id       INTEGER NOT NULL,
    entry_date      TEXT NOT NULL,       -- ISO date
    crop_name       TEXT NOT NULL,
    activity        TEXT NOT NULL,
    category        TEXT NOT NULL,
    expense_amount  REAL DEFAULT 0.0,
    income_amount   REAL DEFAULT 0.0,
    notes           TEXT,
    season          TEXT,
    sync_status     TEXT DEFAULT 'pending',  -- pending|synced|conflict
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX ix_local_diary_sync ON diary_entries(sync_status);
CREATE INDEX ix_local_diary_season ON diary_entries(season);
```

#### `weather_cache`
```sql
CREATE TABLE weather_cache (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude        REAL NOT NULL,
    longitude       REAL NOT NULL,
    forecast_date   TEXT NOT NULL,       -- ISO date
    temp_max        REAL,
    temp_min        REAL,
    precipitation   REAL,
    humidity        REAL,
    wind_speed      REAL,
    description     TEXT,
    fetched_at      TEXT DEFAULT (datetime('now')),
    expires_at      TEXT NOT NULL        -- Cache expiry (6 hours from fetch)
);

CREATE INDEX ix_weather_cache_location ON weather_cache(latitude, longitude);
CREATE INDEX ix_weather_cache_expiry ON weather_cache(expires_at);
```

#### `price_cache`
```sql
CREATE TABLE price_cache (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_name       TEXT NOT NULL,
    mandi_name      TEXT NOT NULL,
    state           TEXT NOT NULL,
    district        TEXT,
    modal_price     REAL NOT NULL,
    min_price       REAL,
    max_price       REAL,
    price_date      TEXT NOT NULL,
    fetched_at      TEXT DEFAULT (datetime('now')),
    expires_at      TEXT NOT NULL        -- Cache expiry (24 hours)
);

CREATE INDEX ix_price_cache_crop ON price_cache(crop_name);
CREATE INDEX ix_price_cache_expiry ON price_cache(expires_at);
```

#### `sync_metadata`
```sql
CREATE TABLE sync_metadata (
    table_name      TEXT PRIMARY KEY,    -- e.g., 'diary_entries'
    last_sync_at    TEXT,                -- ISO 8601 timestamp
    last_server_id  INTEGER,            -- Highest server ID synced
    sync_version    INTEGER DEFAULT 0   -- Incremental version counter
);
```

#### `pending_queue`
```sql
CREATE TABLE pending_queue (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    action          TEXT NOT NULL,       -- CREATE|UPDATE|DELETE
    table_name      TEXT NOT NULL,
    record_id       INTEGER NOT NULL,    -- Local SQLite row ID
    payload         TEXT NOT NULL,       -- JSON serialized data
    retry_count     INTEGER DEFAULT 0,
    created_at      TEXT DEFAULT (datetime('now')),
    status          TEXT DEFAULT 'pending'  -- pending|processing|failed|completed
);

CREATE INDEX ix_pending_queue_status ON pending_queue(status);
```

### Sync Protocol

#### 1. Client → Server (Upload)

```
Trigger: App comes online / manual refresh / every 30 minutes when connected

Algorithm:
1. Query pending_queue WHERE status = 'pending' ORDER BY created_at ASC
2. For each queued action:
   a. POST/PUT/DELETE to server API
   b. On success:
      - Update local record: sync_status = 'synced', server_id = response.id
      - Remove from pending_queue (or mark 'completed')
   c. On failure (network):
      - Increment retry_count
      - Exponential backoff: next_retry = 2^retry_count minutes
      - After 5 failures: mark 'failed', notify user
   d. On conflict (409):
      - Mark sync_status = 'conflict'
      - Store both versions, ask user to resolve
3. Update sync_metadata.last_sync_at
```

#### 2. Server → Client (Download)

```
Trigger: App startup / manual refresh / every 6 hours for weather

Algorithm:
1. GET /api/v1/diary/{farmer_id}?updated_after={last_sync_at}
   - Download only records changed since last sync
2. For weather: GET /api/v1/weather/forecast → update weather_cache
3. For prices: GET /api/v1/mandi/prices → update price_cache
4. Clear expired cache entries:
   DELETE FROM weather_cache WHERE expires_at < datetime('now')
   DELETE FROM price_cache WHERE expires_at < datetime('now')
5. Update sync_metadata
```

#### 3. Conflict Resolution

```
Strategy: Last-Writer-Wins with user confirmation for diary entries

Cases:
├── Same diary entry edited on two devices:
│   → Show both versions, let farmer choose
├── Server record deleted, client edited:
│   → Re-create on server (farmer's edit takes priority)
├── Price data conflict:
│   → Server always wins (authoritative source)
└── Profile conflict:
│   → Latest updated_at wins
```

### Data Flow Diagram

```
Farmer opens app
       │
       ▼
┌─ Is there internet? ──────────────────────────────┐
│   YES                                          NO  │
│   │                                             │  │
│   ▼                                             ▼  │
│ Sync pending_queue                 Load from    │  │
│ Download updates                   SQLite cache │  │
│ Refresh weather                    Show cached  │  │
│ Refresh prices                     weather      │  │
│ Store in SQLite                    Show cached  │  │
│   │                                prices       │  │
│   ▼                                  │          │  │
│ Show fresh data ◄────────────────────┘          │  │
│                                                  │  │
│ Farmer creates diary entry                       │  │
│   │                                              │  │
│   ▼                                              │  │
│ Save to SQLite immediately                       │  │
│   │                                              │  │
│   ▼                                              │  │
│ ┌─ Online? ────────────────────────┐             │  │
│ │  YES: POST to server             │             │  │
│ │  NO:  Add to pending_queue       │             │  │
│ └──────────────────────────────────┘             │  │
└──────────────────────────────────────────────────┘
```

### Storage Estimates

| Data Type | Records (per farmer) | Size Estimate |
|-----------|---------------------|---------------|
| Farmer profile | 1 | <1 KB |
| Diary entries (1 year) | ~100–200 entries | ~50 KB |
| Weather cache (10 days) | 10 rows | ~2 KB |
| Price cache (7 days × 10 crops × 5 mandis) | ~350 rows | ~35 KB |
| Crop database | ~50 crops × 5 stages | ~25 KB |
| Disease database | ~50 diseases | ~50 KB |
| Scheme database | ~20 schemes | ~10 KB |
| **Total SQLite DB size** | — | **<1 MB** |

> The entire local database fits comfortably on even 16GB phones, with negligible storage impact.

---

## Migration Strategy (Alembic)

The project uses Alembic for database migrations, configured in `backend/alembic.ini`.

```bash
# Create a new migration
cd backend
alembic revision --autogenerate -m "description of change"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current state
alembic current
```

### SQLAlchemy ORM Mapping

All models inherit from a shared `Base` declarative base defined in `backend/app/models/database.py`:

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Database URL: SQLite (dev) or PostgreSQL (prod)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aifarmer.db")
```
