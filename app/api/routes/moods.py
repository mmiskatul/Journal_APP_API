from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.mood import MoodCreate, MoodOut, MoodStats
from app.services import mood as mood_service

router = APIRouter()


@router.post("/", response_model=MoodOut)
def create_mood(
    payload: MoodCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return mood_service.create_mood(db, current_user, payload.model_dump())


@router.get("/", response_model=list[MoodOut])
def list_moods(db=Depends(get_db), current_user=Depends(get_current_active_user)):
    return mood_service.list_moods(db, current_user)


@router.get("/stats", response_model=MoodStats)
def stats(db=Depends(get_db), current_user=Depends(get_current_active_user)):
    return mood_service.mood_stats(db, current_user)
