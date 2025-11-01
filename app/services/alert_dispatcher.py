import httpx
import logging
from app.config import settings

logger = logging.getLogger("alert_dispatcher")
logger.setLevel(logging.INFO)

class AlertDispatcher:
    @staticmethod
    def send_alert(payload: dict):
        try:
            with httpx.Client(timeout=5.0) as client:
                r = client.post(settings.ALERT_1C_URL, json=payload)
                r.raise_for_status()
                logger.info("Alert sent to 1C: %s", payload)
        except Exception as e:
            logger.exception("Failed to send alert to 1C: %s", e)
