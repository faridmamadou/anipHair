from fastapi import APIRouter, Header, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from services.workflow_service import WorkflowService
import logging
import os

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

from config import WEBHOOK_SECRET

@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    token: str = None,
    db: Session = Depends(get_db)
):
    # Security check using Token-in-URL approach
    if WEBHOOK_SECRET and token != WEBHOOK_SECRET:
        logger.warning("Invalid webhook token received")
        raise HTTPException(status_code=401, detail="Invalid token")

    payload = await request.json()
    logger.info(f"Received WhatsApp webhook: {payload}")
    
    workflow_service = WorkflowService(db)
    result = await workflow_service.handle_whatsapp_event(payload)
    
    return {"status": "success", "processed": result is not None}
