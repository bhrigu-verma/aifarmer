from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.database import get_db
from app.models.farmer import Farmer
from app.services.diary_service import create_entry, get_entries, get_season_summary
from app.schemas.diary import DiaryEntryCreate, DiaryEntryResponse, SeasonSummary

router = APIRouter()


@router.post("/{farmer_id}", response_model=DiaryEntryResponse, status_code=201)
def add_entry(
    farmer_id: int, entry: DiaryEntryCreate, db: Session = Depends(get_db)
):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    db_entry = create_entry(db, farmer_id, entry)
    return db_entry


@router.get("/{farmer_id}", response_model=List[DiaryEntryResponse])
def list_entries(
    farmer_id: int,
    season: Optional[str] = Query(None),
    crop_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return get_entries(db, farmer_id, season, crop_name)


@router.get("/{farmer_id}/summary", response_model=SeasonSummary)
def season_summary(
    farmer_id: int,
    season: str = Query(...),
    crop_name: str = Query(...),
    db: Session = Depends(get_db),
):
    return get_season_summary(db, farmer_id, season, crop_name)
