from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.messaging import (
    compute_day_index,
    get_customer_message_status,
    get_template_for_day,
    list_active_customers,
    log_message,
)
from app.services.whatsapp import send_message


class MessageScheduler:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler(timezone="UTC")

    def start(self) -> None:
        self.scheduler.add_job(self.send_daily_messages, "cron", hour=9, minute=0)
        self.scheduler.start()

    def shutdown(self) -> None:
        self.scheduler.shutdown(wait=False)

    def send_daily_messages(self) -> None:
        today = date.today()
        for customer in list_active_customers():
            day_index = compute_day_index(date.fromisoformat(customer["purchase_date"]), today)
            if day_index < 0 or day_index > 34:
                continue
            if get_customer_message_status(customer["id"], day_index):
                continue
            template = get_template_for_day(day_index)
            if not template:
                log_message(customer["id"], day_index, "skipped", "Missing template")
                continue
            result = send_message(customer["phone"], template)
            status = "sent" if result.success else "failed"
            log_message(customer["id"], day_index, status, result.detail)
