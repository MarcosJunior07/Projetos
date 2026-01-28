from dataclasses import dataclass


@dataclass
class WhatsAppResult:
    success: bool
    detail: str


def send_message(phone: str, body: str) -> WhatsAppResult:
    if not phone or not body:
        return WhatsAppResult(success=False, detail="Missing phone or body")

    return WhatsAppResult(success=True, detail="Queued for delivery")
