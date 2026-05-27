from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from ..dependencies import get_db, get_current_user
from ..models.users import User
from ..services.export_service import generate_customers_csv, generate_executive_pdf

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/customers/csv")
async def export_customers_csv(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export the list of segmented customers as a CSV file stream.
    """
    try:
        csv_io = await generate_customers_csv(db)
        return StreamingResponse(
            csv_io,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=segmented_customers.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV: {str(e)}")

@router.get("/report/pdf")
async def export_report_pdf(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export the executive business report as a styled PDF file stream.
    """
    try:
        pdf_io = await generate_executive_pdf(db)
        return StreamingResponse(
            pdf_io,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=customeriq_executive_report.pdf"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
