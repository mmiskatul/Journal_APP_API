from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_event(db: Session, user_id: int | None, action: str, ip: str | None, user_agent: str | None, metadata: dict | None = None) -> None:
    log = AuditLog(user_id=user_id, action=action, ip_address=ip, user_agent=user_agent, metadata=metadata or None)
    db.add(log)
    db.commit()
