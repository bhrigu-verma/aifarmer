from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from app.models.database import Base


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    name_hi = Column(String(100))
    season = Column(String(20), nullable=False)  # kharif, rabi, zaid
    duration_days = Column(Integer)
    water_requirement = Column(String(20))  # low, medium, high
    suitable_soil_types = Column(JSON)
    min_temperature = Column(Float)
    max_temperature = Column(Float)
    avg_yield_per_acre = Column(Float)
    avg_cost_per_acre = Column(Float)
    avg_revenue_per_acre = Column(Float)
    is_msp_crop = Column(Boolean, default=False)
    msp_price_per_quintal = Column(Float)


class CropStage(Base):
    __tablename__ = "crop_stages"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, nullable=False, index=True)
    stage_name = Column(String(50), nullable=False)
    stage_order = Column(Integer, nullable=False)
    duration_days = Column(Integer)
    fertiliser_type = Column(String(100))
    fertiliser_quantity_kg_per_acre = Column(Float)
    water_frequency_days = Column(Integer)
    water_quantity_litres_per_acre = Column(Float)
    pesticide_name = Column(String(100))
    pesticide_quantity_ml_per_acre = Column(Float)
    care_instructions = Column(String(500))
    care_instructions_hi = Column(String(500))
