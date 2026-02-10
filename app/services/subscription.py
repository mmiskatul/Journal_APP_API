from datetime import datetime, timezone

import stripe
from fastapi import HTTPException

from app.core.config import settings
from app.core.mongo import serialize_id, to_object_id

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


def create_checkout_session(db, user: dict, plan_id: str) -> str:
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


def handle_webhook(db, payload: bytes, sig_header: str | None) -> None:
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

        user = db.users.find_one({"email": email})
        if not user:
            return
        sub = db.subscriptions.find_one({"user_id": str(user["_id"])})
        update = {
            "user_id": str(user["_id"]),
            "stripe_customer_id": customer_id,
            "stripe_subscription_id": subscription.get("id"),
            "plan_id": price_id,
            "status": status or "inactive",
            "current_period_end": current_period_end,
            "updated_at": datetime.now(timezone.utc),
        }
        if sub:
            db.subscriptions.update_one({"_id": sub["_id"]}, {"$set": update})
        else:
            db.subscriptions.insert_one(update)

        db.users.update_one({"_id": user["_id"]}, {"$set": {"is_premium": status == "active"}})

    if event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")

        sub = db.subscriptions.find_one({"stripe_customer_id": customer_id})
        if sub:
            db.subscriptions.update_one({"_id": sub["_id"]}, {"$set": {"status": "canceled"}})
            if sub.get("user_id"):
                db.users.update_one({"_id": to_object_id(sub["user_id"])}, {"$set": {"is_premium": False}})


def get_subscription(db, user: dict) -> dict | None:
    sub = db.subscriptions.find_one({"user_id": user["id"]})
    return serialize_id(sub) if sub else None


def cancel_subscription(db, user: dict) -> None:
    sub = db.subscriptions.find_one({"user_id": user["id"]})
    if not sub or not sub.get("stripe_subscription_id"):
        raise HTTPException(status_code=404, detail="Subscription not found")

    stripe.Subscription.delete(sub["stripe_subscription_id"])
    db.subscriptions.update_one({"_id": sub["_id"]}, {"$set": {"status": "canceled"}})
    db.users.update_one({"_id": to_object_id(sub["user_id"])}, {"$set": {"is_premium": False}})
