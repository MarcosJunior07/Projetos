from datetime import date

from fastapi import FastAPI, HTTPException

from app.db import init_db
from app.models import HotmartWebhookPayload, ManualMessageRequest, TemplateUpsertRequest
from app.services.hotmart import mark_refunded, upsert_customer
from app.services.messaging import log_message, upsert_template
from app.services.scheduler import MessageScheduler
from app.services.whatsapp import send_message

app = FastAPI(title="Hotmart + WhatsApp Automation")

scheduler = MessageScheduler()


@app.on_event("startup")
async def on_startup() -> None:
    init_db()
    scheduler.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    scheduler.shutdown()


@app.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}


@app.post("/webhooks/hotmart/purchase")
async def hotmart_purchase(payload: HotmartWebhookPayload) -> dict:
    customer_id = upsert_customer(
        payload.email,
        payload.phone,
        payload.purchase_date,
        payload.order_id,
    )
    return {"status": "accepted", "customer_id": customer_id}


@app.post("/webhooks/hotmart/refund")
async def hotmart_refund(payload: HotmartWebhookPayload) -> dict:
    mark_refunded(payload.email)
    return {"status": "refunded"}


@app.post("/admin/templates")
async def update_template(payload: TemplateUpsertRequest) -> dict:
    upsert_template(payload.day_index, payload.body)
    return {"status": "updated", "day_index": payload.day_index}


@app.post("/admin/messages/manual")
async def manual_message(payload: ManualMessageRequest) -> dict:
    if payload.body.strip() == "":
        raise HTTPException(status_code=400, detail="Message body cannot be empty")
    result = send_message("manual", payload.body)
    status = "sent" if result.success else "failed"
    log_message(payload.customer_id, 0, status, result.detail)
    return {"status": status, "detail": result.detail}


@app.get("/admin/daily-preview")
async def daily_preview(date_override: date | None = None) -> dict:
    target_date = date_override or date.today()
    return {"date": target_date.isoformat(), "note": "Preview endpoint stub"}
