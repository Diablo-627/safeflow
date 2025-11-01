# app/services/alert_dispatcher.py
import httpx
import logging
from app.config import settings

logger = logging.getLogger("alert_dispatcher")
logger.setLevel(logging.INFO)

class AlertDispatcher:
    @staticmethod
    def send_alert(payload: dict):
        """
        Synchronously send alert to 1C endpoint.
        Failures are logged and swallowed (so alerts don't break flow).
        """
        url = settings.ALERT_1C_URL
        if not url:
            logger.info("ALERT_1C_URL not set; skipping alert: %s", payload)
            return
        try:
            with httpx.Client(timeout=5.0) as client:
                r = client.post(url, json=payload)
                r.raise_for_status()
                logger.info("Alert dispatched: %s -> %s", payload, r.status_code)
        except Exception as exc:
            logger.exception("Failed to dispatch alert: %s", exc)
