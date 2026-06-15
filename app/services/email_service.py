import logging
import urllib.request
import json
from flask import current_app
from app.models import User

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    template_name: str = None,
    body: str = None,
    context: dict = None,
) -> None:
    """
    Delegate email sending to the centralized Notification Engine.

    Args:
        to_email: Recipient email address
        subject: Email subject
        template_name: Name of template (without extension)
        body: Plain text body (fallback if template_name not provided)
        context: Dictionary of variables for template rendering
    """
    try:
        # Ensure parameters are strings
        to_email = str(to_email) if to_email else ""
        subject = str(subject) if subject else ""

        current_app.logger.info(
            f"[EMAIL] send_email() called - To: {to_email}, "
            f"Subject: {subject}, Template: {template_name}"
        )

        # 1. Resolve user ID from email, or fallback to default system UUID
        user_id = "00000000-0000-0000-0000-000000000000"
        try:
            user = User.query.filter_by(email=to_email).first()
            if user:
                user_id = str(user.id)
        except Exception as db_err:
            current_app.logger.warning(f"[EMAIL] Failed to lookup user ID from database: {str(db_err)}")

        # 2. Map local template name to eventType
        event_type = "GENERIC"
        if template_name:
            event_type = f"AUTH_{template_name.upper()}"

        # 3. Build HTTP Payload
        payload = {
            "userId": user_id,
            "title": subject,
            "message": body or "",
            "channels": ["EMAIL"],
            "severity": "MEDIUM",
            "category": "AUTH",
            "eventType": event_type,
            "context": {
                "email": to_email,
                **(context or {})
            }
        }

        # 4. Dispatch POST request via urllib.request
        notification_url = f"{current_app.config['NOTIFICATION_SERVICE_URL']}/api/v1/notifications"
        current_app.logger.info(f"[EMAIL] Delegating email notification to: {notification_url}")

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            notification_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            response_body = response.read().decode("utf-8")
            current_app.logger.info(f"[EMAIL] Centralized engine responded with status {status_code}: {response_body}")

    except Exception as e:
        current_app.logger.error(
            f"[EMAIL] Unexpected error delegating email to notification engine: {type(e).__name__}: {str(e)}"
        )
        current_app.logger.exception("[EMAIL] Full exception trace:")

