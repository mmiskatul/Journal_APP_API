from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.goal import GoalCreate, GoalOut, GoalStatusUpdate, GoalUpdate
from app.services import goal as goal_service

router = APIRouter()


@router.post("/", response_model=GoalOut)
def create_goal(
    payload: GoalCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return goal_service.create_goal(db, current_user, payload.model_dump())


@router.get("/", response_model=list[GoalOut])
def list_goals(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    return goal_service.list_goals(db, current_user)


@router.get("/{goal_id}", response_model=GoalOut)
def get_goal(goal_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    return goal_service.get_goal(db, current_user, goal_id)


@router.put("/{goal_id}", response_model=GoalOut)
def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    goal = goal_service.get_goal(db, current_user, goal_id)
    return goal_service.update_goal(db, goal, payload.model_dump())


@router.patch("/{goal_id}/status", response_model=GoalOut)
def update_status(
    goal_id: int,
    payload: GoalStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    goal = goal_service.get_goal(db, current_user, goal_id)
    return goal_service.update_goal(db, goal, {"status": payload.status})


@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    goal = goal_service.get_goal(db, current_user, goal_id)
    goal_service.delete_goal(db, goal)
    return {"message": "Goal deleted"}
