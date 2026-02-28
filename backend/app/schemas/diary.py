from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class DiaryEntryCreate(BaseModel):
    crop_name: str = Field(..., max_length=100)
    activity: str = Field(..., max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    expense_amount: float = Field(0.0, ge=0)
    income_amount: float = Field(0.0, ge=0)
    notes: Optional[str] = Field(None, max_length=500)
    season: Optional[str] = Field(None, max_length=20)
    entry_date: Optional[date] = None


class DiaryEntryResponse(BaseModel):
    id: int
    farmer_id: int
    entry_date: date
    crop_name: str
    activity: str
    category: Optional[str]
    expense_amount: float
    income_amount: float
    notes: Optional[str]
    season: Optional[str]

    class Config:
        from_attributes = True


class SeasonSummary(BaseModel):
    season: str
    crop_name: str
    total_expenses: float
    total_income: float
    net_profit: float
    entries_count: int
    expense_breakdown: dict
