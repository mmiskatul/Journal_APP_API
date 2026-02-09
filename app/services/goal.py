from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.models.user import User


def create_goal(db: Session, user: User, data: dict) -> Goal:
    goal = Goal(user_id=user.id, **data)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def list_goals(db: Session, user: User) -> list[Goal]:
    return db.query(Goal).filter(Goal.user_id == user.id).order_by(Goal.created_at.desc()).all()


def get_goal(db: Session, user: User, goal_id: int) -> Goal:
    goal = db.query(Goal).filter(Goal.user_id == user.id, Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


def update_goal(db: Session, goal: Goal, data: dict) -> Goal:
    for key, value in data.items():
        if value is not None:
            setattr(goal, key, value)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def delete_goal(db: Session, goal: Goal) -> None:
    db.delete(goal)
    db.commit()
