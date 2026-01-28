from datetime import date
from typing import Optional

from app.db import get_connection


def upsert_customer(email: str, phone: str, purchase_date: date, order_id: Optional[str]) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO customers (email, phone, purchase_date, status, hotmart_order_id)
            VALUES (?, ?, ?, 'active', ?)
            ON CONFLICT(email) DO UPDATE SET
                phone = excluded.phone,
                purchase_date = excluded.purchase_date,
                status = 'active',
                hotmart_order_id = excluded.hotmart_order_id
            """,
            (email, phone, purchase_date.isoformat(), order_id),
        )
        if cursor.lastrowid:
            customer_id = cursor.lastrowid
        else:
            customer_id = connection.execute(
                "SELECT id FROM customers WHERE email = ?",
                (email,),
            ).fetchone()["id"]
        connection.commit()
    return customer_id


def mark_refunded(email: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "UPDATE customers SET status = 'refunded' WHERE email = ?",
            (email,),
        )
        connection.commit()
