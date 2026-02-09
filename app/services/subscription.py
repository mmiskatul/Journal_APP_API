from datetime import datetime, timezone

import stripe
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.subscription import Subscription
from app.models.user import User

stripe.api_key = settings.stripe_api_key


def get_plans() -> list[dict]:
    return [
        {
            "id": "basic",
            "name": "Basic",
            "price_id": settings.stripe_price_basic,
            "price_display": "$4.99/mo",
        },
        {
            "id": "premium",
            "name": "Premium",
            "price_id": settings.stripe_price_premium,
            "price_display": "$9.99/mo",
        },
    ]


def create_checkout_session(db: Session, user: User, plan_id: str) -> str:
    plans = {plan["id"]: plan for plan in get_plans()}
    if plan_id not in plans:
        raise HTTPException(status_code=400, detail="Invalid plan")

    price_id = plans[plan_id]["price_id"]
    if not price_id:
        raise HTTPException(status_code=400, detail="Stripe price not configured")

    session = stripe.checkout.Session.create(
        customer_email=user.email,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=settings.frontend_success_url,
        cancel_url=settings.frontend_cancel_url,
    )

    return session.url


def handle_webhook(db: Session, payload: bytes, sig_header: str | None) -> None:
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")

    event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)

    if event["type"] in ["customer.subscription.created", "customer.subscription.updated"]:
        subscription = event["data"]["object"]
        email = subscription.get("customer_email")
        customer_id = subscription.get("customer")
        status = subscription.get("status")
        current_period_end = datetime.fromtimestamp(subscription.get("current_period_end"), tz=timezone.utc)
        price_id = None
        if subscription.get("items") and subscription["items"]["data"]:
            price_id = subscription["items"]["data"][0]["price"]["id"]

        user = db.query(User).filter(User.email == email).first()
        if not user:
            return

        sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        if not sub:
            sub = Subscription(user_id=user.id)

        sub.stripe_customer_id = customer_id
        sub.stripe_subscription_id = subscription.get("id")
        sub.plan_id = price_id
        sub.status = status or "inactive"
        sub.current_period_end = current_period_end

        user.is_premium = status == "active"

        db.add(sub)
        db.add(user)
        db.commit()

    if event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")

        sub = db.query(Subscription).filter(Subscription.stripe_customer_id == customer_id).first()
        if sub:
            sub.status = "canceled"
            if sub.user:
                sub.user.is_premium = False
                db.add(sub.user)
            db.add(sub)
            db.commit()


def get_subscription(db: Session, user: User) -> Subscription | None:
    return db.query(Subscription).filter(Subscription.user_id == user.id).first()


def cancel_subscription(db: Session, user: User) -> None:
    sub = get_subscription(db, user)
    if not sub or not sub.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="Subscription not found")

    stripe.Subscription.delete(sub.stripe_subscription_id)
    sub.status = "canceled"
    user.is_premium = False

    db.add(sub)
    db.add(user)
    db.commit()
