from app.tasks.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_push_notification(self, user_id: str, title: str, body: str, data: dict = None):
    """Send FCM push notification to a user."""
    try:
        # TODO: integrate with Firebase Admin SDK
        logger.info(f"Push notification -> user={user_id} title={title}")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task
def send_email_notification(to: str, subject: str, body: str):
    """Send transactional email via SMTP."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from app.core.config import settings

        if not settings.SMTP_USER:
            logger.warning("SMTP not configured, skipping email")
            return

        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_USER
        msg["To"] = to

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, [to], msg.as_string())

        logger.info(f"Email sent to {to}")
    except Exception as e:
        logger.error(f"Email error: {e}")


@celery_app.task
def notify_service_accepted(professional_name: str, client_fcm: str | None, client_email: str):
    if client_fcm:
        send_push_notification.delay(
            user_id="",
            title="Serviço Aceito! 🎉",
            body=f"{professional_name} aceitou sua solicitação.",
        )
    send_email_notification.delay(
        to=client_email,
        subject="Seu serviço foi aceito!",
        body=f"<p><strong>{professional_name}</strong> aceitou sua solicitação de serviço.</p>",
    )


@celery_app.task
def notify_service_completed(service_id: str, client_email: str):
    send_email_notification.delay(
        to=client_email,
        subject="Serviço concluído — Avalie agora!",
        body=f"<p>Seu serviço foi concluído. <a href='#'>Clique aqui para avaliar</a>.</p>",
    )
