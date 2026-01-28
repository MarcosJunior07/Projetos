from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class HotmartWebhookPayload(BaseModel):
    email: str
    phone: str
    purchase_date: date
    order_id: Optional[str] = None


class ManualMessageRequest(BaseModel):
    customer_id: int = Field(..., ge=1)
    body: str


class TemplateUpsertRequest(BaseModel):
    day_index: int = Field(..., ge=0, le=34)
    body: str
