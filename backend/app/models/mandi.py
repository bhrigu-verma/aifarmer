from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from datetime import datetime, timezone, date

from app.models.database import Base


class MandiPrice(Base):
    __tablename__ = "mandi_prices"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(100), nullable=False, index=True)
    mandi_name = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    min_price = Column(Float)
    max_price = Column(Float)
    modal_price = Column(Float, nullable=False)
    price_unit = Column(String(20), default="INR/quintal")
    price_date = Column(Date, default=date.today, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
