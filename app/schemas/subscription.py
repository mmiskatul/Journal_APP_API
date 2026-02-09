from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlanOut(BaseModel):
    id: str
    name: str
    price_id: str
    price_display: str


class CheckoutRequest(BaseModel):
    plan_id: str


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan_id: str | None = None
    status: str
    current_period_end: datetime | None = None
