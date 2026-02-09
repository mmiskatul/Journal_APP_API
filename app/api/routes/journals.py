from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.journal import JournalCreate, JournalOut, JournalUpdate
from app.services import journal as journal_service

router = APIRouter()


@router.post("/", response_model=JournalOut)
def create_journal(
    payload: JournalCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return journal_service.create_entry(db, current_user, payload.model_dump())


@router.get("/", response_model=list[JournalOut])
def list_journals(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return journal_service.list_entries(db, current_user, start_date, end_date, category)


@router.get("/{entry_id}", response_model=JournalOut)
def get_journal(entry_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    return journal_service.get_entry(db, current_user, entry_id)


@router.put("/{entry_id}", response_model=JournalOut)
def update_journal(
    entry_id: int,
    payload: JournalUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    entry = journal_service.get_entry(db, current_user, entry_id)
    return journal_service.update_entry(db, entry, payload.model_dump())


@router.delete("/{entry_id}")
def delete_journal(entry_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    entry = journal_service.get_entry(db, current_user, entry_id)
    journal_service.delete_entry(db, entry)
    return {"message": "Journal entry deleted"}
