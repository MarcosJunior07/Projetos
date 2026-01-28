from datetime import date, datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import db
from app.services import hotmart, scheduler

app = FastAPI(title="Hotmart WhatsApp Automations")

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup() -> None:
    db.init_db()
    scheduler.seed_default_messages()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/webhooks/hotmart")
def hotmart_webhook(payload: dict) -> dict[str, str | int]:
    return hotmart.handle_webhook(payload)


@app.post("/messages/template")
def create_message_template(payload: dict) -> dict[str, str | int]:
    day_offset = int(payload.get("day_offset", 0))
    body = payload.get("body", "")
    template_id = db.execute(
        "INSERT INTO messages (day_offset, body, created_at) VALUES (?, ?, ?)",
        (day_offset, body, datetime.utcnow().isoformat()),
    )
    return {"status": "created", "id": template_id}


@app.post("/messages/dispatch")
def dispatch_messages(payload: dict | None = None) -> dict[str, list[dict[str, str]]]:
    payload = payload or {}
    date_value = payload.get("date")
    target_date = date.fromisoformat(date_value) if date_value else None
    results = scheduler.dispatch_daily_messages(target_date)
    return {"results": results}


@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request) -> HTMLResponse:
    customers = db.fetch_all(
        "SELECT id, name, phone, purchase_date, status, last_sent_at FROM customers"
    )
    messages = db.fetch_all("SELECT day_offset, body FROM messages ORDER BY day_offset")
    logs = db.fetch_all(
        "SELECT event, detail, created_at FROM logs ORDER BY created_at DESC LIMIT 20"
    )
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "customers": customers,
            "messages": messages,
            "logs": logs,
        },
    )
