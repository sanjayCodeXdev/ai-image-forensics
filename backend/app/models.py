"""SQLAlchemy ORM models for the analyses table."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    analysis_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, default=lambda: str(uuid.uuid4())
    )
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[int] = mapped_column(Integer)
    file_type: Mapped[str] = mapped_column(String(50))
    image_width: Mapped[int] = mapped_column(Integer, nullable=True)
    image_height: Mapped[int] = mapped_column(Integer, nullable=True)

    # Final result
    final_result: Mapped[str] = mapped_column(String(50), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)
    ai_probability: Mapped[float] = mapped_column(Float, nullable=True)
    real_probability: Mapped[float] = mapped_column(Float, nullable=True)

    # Sub-analysis statuses
    metadata_status: Mapped[str] = mapped_column(String(100), nullable=True)
    provenance_status: Mapped[str] = mapped_column(String(100), nullable=True)
    watermark_status: Mapped[str] = mapped_column(String(100), nullable=True)
    forensic_score: Mapped[float] = mapped_column(Float, nullable=True)

    # Model info
    model_name: Mapped[str] = mapped_column(String(100), nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=True)

    # Full JSON blob of all sub-results
    analysis_json: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
