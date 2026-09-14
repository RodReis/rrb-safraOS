from __future__ import annotations

import smtplib
from email.message import EmailMessage

from sqlalchemy import create_engine, text

from safraos_api.settings import Settings
from safraos_worker.app import celery_app


@celery_app.task(autoretry_for=(smtplib.SMTPException, OSError), max_retries=3)
def send_identity_email(outbox_id: str) -> str:
    settings = Settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    with engine.begin() as conn:
        row = (
            conn.execute(
                text(
                    """
                    SELECT id, payload, status
                    FROM identity_outbox
                    WHERE id = :id
                    FOR UPDATE
                    """
                ),
                {"id": outbox_id},
            )
            .mappings()
            .first()
        )
        if row is None:
            return "missing"
        if row["status"] == "sent":
            return "already_sent"
        payload = row["payload"]
        message = EmailMessage()
        message["From"] = "nao-responda@safraos.local"
        message["To"] = payload["to"]
        message["Subject"] = payload["subject"]
        message.set_content(f"{payload['subject']}\n\n{payload['url']}\n")
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.send_message(message)
        conn.execute(
            text(
                """
                UPDATE identity_outbox
                SET status = 'sent', sent_at = now(), attempts = attempts + 1
                WHERE id = :id
                """
            ),
            {"id": outbox_id},
        )
    return "sent"
