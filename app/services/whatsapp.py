from datetime import datetime
from typing import Any

from app import db


def send_message(phone: str, body: str, customer_id: int | None = None) -> dict[str, Any]:
    payload = {
        "to": phone,
        "body": body,
        "status": "sent",
        "sent_at": datetime.utcnow().isoformat(),
    }
    db.execute(
        "INSERT INTO logs (customer_id, event, detail, created_at) VALUES (?, ?, ?, ?)",
        (
            customer_id,
            "whatsapp_dispatch",
            f"Mensagem enviada para {phone}: {body}",
            payload["sent_at"],
        ),
    )
    return payload
