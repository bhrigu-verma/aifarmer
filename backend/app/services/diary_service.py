from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.models.diary import DiaryEntry
from app.schemas.diary import DiaryEntryCreate, DiaryEntryResponse, SeasonSummary


def create_entry(db: Session, farmer_id: int, entry: DiaryEntryCreate) -> DiaryEntry:
    db_entry = DiaryEntry(
        farmer_id=farmer_id,
        entry_date=entry.entry_date or date.today(),
        crop_name=entry.crop_name,
        activity=entry.activity,
        category=entry.category,
        expense_amount=entry.expense_amount,
        income_amount=entry.income_amount,
        notes=entry.notes,
        season=entry.season,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_entries(
    db: Session,
    farmer_id: int,
    season: Optional[str] = None,
    crop_name: Optional[str] = None,
) -> List[DiaryEntry]:
    query = db.query(DiaryEntry).filter(DiaryEntry.farmer_id == farmer_id)
    if season:
        query = query.filter(DiaryEntry.season == season)
    if crop_name:
        query = query.filter(DiaryEntry.crop_name == crop_name)
    return query.order_by(DiaryEntry.entry_date.desc()).all()


def get_season_summary(
    db: Session, farmer_id: int, season: str, crop_name: str
) -> SeasonSummary:
    entries = (
        db.query(DiaryEntry)
        .filter(
            DiaryEntry.farmer_id == farmer_id,
            DiaryEntry.season == season,
            DiaryEntry.crop_name == crop_name,
        )
        .all()
    )

    total_expenses = sum(e.expense_amount for e in entries)
    total_income = sum(e.income_amount for e in entries)
    breakdown: dict = {}
    for e in entries:
        cat = e.category or "other"
        breakdown[cat] = breakdown.get(cat, 0) + e.expense_amount

    return SeasonSummary(
        season=season,
        crop_name=crop_name,
        total_expenses=total_expenses,
        total_income=total_income,
        net_profit=total_income - total_expenses,
        entries_count=len(entries),
        expense_breakdown=breakdown,
    )
