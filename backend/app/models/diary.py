from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, date

from app.models.database import Base


class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    entry_date = Column(Date, default=date.today)
    crop_name = Column(String(100), nullable=False)
    activity = Column(String(200), nullable=False)
    category = Column(String(50))  # sowing, irrigation, fertiliser, pesticide, labour, harvest, sale
    expense_amount = Column(Float, default=0.0)
    income_amount = Column(Float, default=0.0)
    notes = Column(String(500))
    season = Column(String(20))  # kharif-2024, rabi-2024
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    farmer = relationship("Farmer", back_populates="diary_entries")
