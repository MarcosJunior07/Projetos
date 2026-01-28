from datetime import date, datetime
from typing import Iterable

from app.db import get_connection


def list_active_customers() -> Iterable[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM customers WHERE status = 'active'"
        ).fetchall()
    return [dict(row) for row in rows]


def get_template_for_day(day_index: int) -> str | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT body FROM message_templates WHERE day_index = ?",
            (day_index,),
        ).fetchone()
    if row:
        return row["body"]
    return None


def upsert_template(day_index: int, body: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO message_templates (day_index, body)
            VALUES (?, ?)
            ON CONFLICT(day_index) DO UPDATE SET body = excluded.body
            """,
            (day_index, body),
        )
        connection.commit()


def log_message(customer_id: int, day_index: int, status: str, detail: str | None) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO message_logs (customer_id, message_day, status, detail, sent_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                customer_id,
                day_index,
                status,
                detail,
                datetime.utcnow().isoformat(),
            ),
        )
        connection.commit()


def compute_day_index(purchase_date: date, today: date) -> int:
    return (today - purchase_date).days


def get_customer_message_status(customer_id: int, day_index: int) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id FROM message_logs
            WHERE customer_id = ? AND message_day = ? AND status = 'sent'
            """,
            (customer_id, day_index),
        ).fetchone()
    return row is not None
