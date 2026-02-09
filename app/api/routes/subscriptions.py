from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import Message
from app.schemas.subscription import CheckoutRequest, PlanOut, SubscriptionOut
from app.services import subscription as subscription_service

router = APIRouter()


@router.get("/plans", response_model=list[PlanOut])
def plans():
    return subscription_service.get_plans()


@router.post("/checkout")
def checkout(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    url = subscription_service.create_checkout_session(db, current_user, payload.plan_id)
    return {"checkout_url": url}


@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    subscription_service.handle_webhook(db, payload, signature)
    return {"received": True}


@router.get("/status", response_model=SubscriptionOut)
def status(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    sub = subscription_service.get_subscription(db, current_user)
    if not sub:
        return SubscriptionOut(status="inactive")
    return sub


@router.post("/cancel", response_model=Message)
def cancel(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    subscription_service.cancel_subscription(db, current_user)
    return Message(message="Subscription canceled")
