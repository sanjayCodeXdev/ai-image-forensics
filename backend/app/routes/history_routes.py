"""History routes — list and delete previous analyses."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Analysis
from app.schemas import HistoryResponse, HistoryItem
from app.config import settings
from app.utils.file_utils import delete_file

router = APIRouter(prefix="/api", tags=["History"])


@router.get("/history", response_model=HistoryResponse)
async def get_history(db: AsyncSession = Depends(get_db)):
    """Return all previous analyses, newest first."""
    result = await db.execute(
        select(Analysis).order_by(Analysis.created_at.desc())
    )
    rows = result.scalars().all()
    items = [HistoryItem.model_validate(r) for r in rows]
    return HistoryResponse(total=len(items), items=items)


@router.delete("/history/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(analysis_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an analysis record and its stored image file."""
    result = await db.execute(
        select(Analysis).where(Analysis.analysis_id == analysis_id)
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Analysis not found.")

    # Delete stored image file
    img_path = settings.UPLOAD_DIR / row.stored_filename
    await delete_file(img_path)

    await db.execute(
        delete(Analysis).where(Analysis.analysis_id == analysis_id)
    )
    await db.commit()
