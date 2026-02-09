from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.audit_log import AuditLog
from app.schemas.admin import AdminResetPasswordResponse, AnalyticsOut, AuditLogOut, SuspendRequest, UserAdminOut
from app.services import admin as admin_service

router = APIRouter()


@router.get("/users", response_model=list[UserAdminOut])
def list_users(db: Session = Depends(get_db), current_admin=Depends(require_admin)):
    return admin_service.list_users(db)


@router.post("/users/{user_id}/suspend", response_model=UserAdminOut)
def suspend_user(
    user_id: int,
    payload: SuspendRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    return admin_service.suspend_user(db, user_id, payload.days)


@router.post("/users/{user_id}/reset-password", response_model=AdminResetPasswordResponse)
def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    temp_password = admin_service.reset_user_password(db, user_id)
    return AdminResetPasswordResponse(temporary_password=temp_password)


@router.get("/analytics", response_model=AnalyticsOut)
def analytics(db: Session = Depends(get_db), current_admin=Depends(require_admin)):
    return admin_service.analytics(db)


@router.get("/logs", response_model=list[AuditLogOut])
def logs(db: Session = Depends(get_db), current_admin=Depends(require_admin)):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all()
