from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.core.deps import require_admin
from app.schemas.admin import AdminResetPasswordResponse, AnalyticsOut, AuditLogOut, SuspendRequest, UserAdminOut
from app.services import admin as admin_service

router = APIRouter()


@router.get("/users", response_model=list[UserAdminOut])
def list_users(db=Depends(get_db), current_admin=Depends(require_admin)):
    return admin_service.list_users(db)


@router.post("/users/{user_id}/suspend", response_model=UserAdminOut)
def suspend_user(
    user_id: str,
    payload: SuspendRequest,
    db=Depends(get_db),
    current_admin=Depends(require_admin),
):
    return admin_service.suspend_user(db, user_id, payload.days)


@router.post("/users/{user_id}/reset-password", response_model=AdminResetPasswordResponse)
def reset_user_password(
    user_id: str,
    db=Depends(get_db),
    current_admin=Depends(require_admin),
):
    temp_password = admin_service.reset_user_password(db, user_id)
    return AdminResetPasswordResponse(temporary_password=temp_password)


@router.get("/analytics", response_model=AnalyticsOut)
def analytics(db=Depends(get_db), current_admin=Depends(require_admin)):
    return admin_service.analytics(db)


@router.get("/logs", response_model=list[AuditLogOut])
def logs(db=Depends(get_db), current_admin=Depends(require_admin)):
    logs_cursor = db.audit_logs.find().sort("created_at", -1).limit(200)
    from app.core.mongo import serialize_id

    return [serialize_id(log) for log in logs_cursor]
