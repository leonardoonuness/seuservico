from app.tasks.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_expired_tokens():
    """Redis TTL handles expiry automatically; this task logs stats."""
    logger.info("Token cleanup check complete (Redis handles TTL).")


@celery_app.task
def recalculate_professional_ratings():
    """Periodic re-aggregation of professional ratings from reviews table."""
    from app.db.session import SessionLocal
    from app.models.professional import Professional
    from app.models.review import Review
    from sqlalchemy import func

    db = SessionLocal()
    try:
        professionals = db.query(Professional).all()
        for prof in professionals:
            result = db.query(
                func.avg(Review.rating),
                func.count(Review.id),
            ).filter(
                Review.professional_id == prof.user_id,
                Review.is_removed == False,
            ).first()
            avg, count = result
            prof.rating = round(float(avg or 0), 2)
            prof.total_ratings = count or 0
        db.commit()
        logger.info(f"Recalculated ratings for {len(professionals)} professionals.")
    finally:
        db.close()
