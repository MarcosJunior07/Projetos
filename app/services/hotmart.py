from datetime import datetime
from typing import Any

from app import db


def handle_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    event = payload.get("event", "purchase")
    customer = payload.get("customer", {})
    name = customer.get("name", "Cliente Hotmart")
    phone = customer.get("phone", "")
    purchase_date = payload.get("purchase_date") or datetime.utcnow().date().isoformat()

    if event == "refund":
        customer_id = payload.get("customer_id")
        if customer_id:
            db.execute(
                "UPDATE customers SET status = ?, last_sent_at = ? WHERE id = ?",
                ("refunded", datetime.utcnow().isoformat(), customer_id),
            )
        db.execute(
            "INSERT INTO logs (customer_id, event, detail, created_at) VALUES (?, ?, ?, ?)",
            (
                customer_id,
                "hotmart_refund",
                "Cliente reembolsado, envio interrompido.",
                datetime.utcnow().isoformat(),
            ),
        )
        return {"status": "refunded"}

    customer_id = db.execute(
        """
        INSERT INTO customers (name, phone, purchase_date, status, last_sent_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            phone,
            purchase_date,
            "active",
            None,
            datetime.utcnow().isoformat(),
        ),
    )
    db.execute(
        "INSERT INTO logs (customer_id, event, detail, created_at) VALUES (?, ?, ?, ?)",
        (
            customer_id,
            "hotmart_purchase",
            f"Compra registrada para {name}.",
            datetime.utcnow().isoformat(),
        ),
    )
    return {"status": "created", "customer_id": customer_id}
