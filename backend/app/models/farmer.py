from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.models.database import Base


class LanguageChoice(str, enum.Enum):
    HINDI = "hi"
    ENGLISH = "en"
    MARATHI = "mr"
    TAMIL = "ta"
    TELUGU = "te"
    KANNADA = "kn"
    BENGALI = "bn"
    GUJARATI = "gu"
    PUNJABI = "pa"
    MALAYALAM = "ml"


class SoilType(str, enum.Enum):
    ALLUVIAL = "alluvial"
    BLACK = "black"
    RED = "red"
    LATERITE = "laterite"
    SANDY = "sandy"
    CLAY = "clay"
    LOAMY = "loamy"


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    state = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    village = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    land_size_acres = Column(Float, nullable=False)
    soil_type = Column(SAEnum(SoilType), nullable=False)
    irrigation_source = Column(String(50))
    language = Column(SAEnum(LanguageChoice), default=LanguageChoice.HINDI)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    diary_entries = relationship("DiaryEntry", back_populates="farmer")
