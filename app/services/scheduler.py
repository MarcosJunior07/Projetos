from datetime import date, datetime
from typing import Iterable

from dateutil.parser import isoparse

from app import db
from app.services import whatsapp


def _days_since_purchase(purchase_date: str, today: date) -> int:
    purchase_day = isoparse(purchase_date).date()
    return (today - purchase_day).days


def _load_messages() -> dict[int, str]:
    rows = db.fetch_all("SELECT day_offset, body FROM messages")
    return {row["day_offset"]: row["body"] for row in rows}


def dispatch_daily_messages(today: date | None = None) -> list[dict[str, str]]:
    current_day = today or date.today()
    customers = db.fetch_all(
        "SELECT id, phone, purchase_date, status FROM customers WHERE status = ?",
        ("active",),
    )
    templates = _load_messages()
    results: list[dict[str, str]] = []

    for customer in customers:
        days = _days_since_purchase(customer["purchase_date"], current_day)
        if days < 0 or days > 34:
            continue
        body = templates.get(days)
        if not body:
            continue
        payload = whatsapp.send_message(customer["phone"], body, customer["id"])
        db.execute(
            "UPDATE customers SET last_sent_at = ? WHERE id = ?",
            (payload["sent_at"], customer["id"]),
        )
        results.append({"customer_id": str(customer["id"]), "status": payload["status"]})

    db.execute(
        "INSERT INTO logs (customer_id, event, detail, created_at) VALUES (?, ?, ?, ?)",
        (
            None,
            "dispatch_run",
            f"Envio diário concluído em {current_day.isoformat()}.",
            datetime.utcnow().isoformat(),
        ),
    )
    return results


def seed_default_messages() -> None:
    existing = db.fetch_all("SELECT id FROM messages LIMIT 1")
    if existing:
        return
    base_message = "Olá! Este é seu acompanhamento do dia {day}."
    db.execute_many(
        "INSERT INTO messages (day_offset, body, created_at) VALUES (?, ?, ?)",
        (
            (
                day,
                base_message.format(day=day + 1),
                datetime.utcnow().isoformat(),
            )
            for day in range(35)
        ),
    )
