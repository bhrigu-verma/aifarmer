from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FarmerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., pattern=r"^\d{10}$")
    state: str = Field(..., max_length=50)
    district: str = Field(..., max_length=50)
    village: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    land_size_acres: float = Field(..., gt=0)
    soil_type: str
    irrigation_source: Optional[str] = None
    language: str = "hi"


class FarmerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    village: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    land_size_acres: Optional[float] = Field(None, gt=0)
    soil_type: Optional[str] = None
    irrigation_source: Optional[str] = None
    language: Optional[str] = None


class FarmerResponse(BaseModel):
    id: int
    name: str
    phone: str
    state: str
    district: str
    village: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    land_size_acres: float
    soil_type: str
    irrigation_source: Optional[str]
    language: str
    created_at: datetime

    class Config:
        from_attributes = True
