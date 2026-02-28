from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import database
from app.routers import (
    farmers,
    weather,
    mandi,
    crops,
    pests,
    inputs,
    schemes,
    diary,
)

app = FastAPI(
    title=settings.app_name,
    description="AI-powered farming assistant for Indian farmers",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    database.create_tables()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.app_name}


app.include_router(farmers.router, prefix="/api/v1/farmers", tags=["Farmers"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["Weather"])
app.include_router(mandi.router, prefix="/api/v1/mandi", tags=["Mandi Prices"])
app.include_router(crops.router, prefix="/api/v1/crops", tags=["Crop Advisor"])
app.include_router(pests.router, prefix="/api/v1/pests", tags=["Pest Detection"])
app.include_router(inputs.router, prefix="/api/v1/inputs", tags=["Input Advisor"])
app.include_router(schemes.router, prefix="/api/v1/schemes", tags=["Government Schemes"])
app.include_router(diary.router, prefix="/api/v1/diary", tags=["Crop Diary"])
