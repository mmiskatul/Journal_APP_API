from datetime import datetime, timezone


def log_event(db, user_id: str | None, action: str, ip: str | None, user_agent: str | None, metadata: dict | None = None) -> None:
    log = {
        "user_id": user_id,
        "action": action,
        "ip_address": ip,
        "user_agent": user_agent,
        "metadata": metadata or None,
        "created_at": datetime.now(timezone.utc),
    }
    db.audit_logs.insert_one(log)
