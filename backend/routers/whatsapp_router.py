from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from services.whatsapp_service import WhatsAppSessionService
from database import get_db
from schemas import AppointmentCreate, Appointment, WhatsAppMessageSend, WhatsAppMessage
from typing import List
from datetime import timedelta
import re
import models
from config import ADMIN_PHONE_NUMBER

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

# WhatsApp Management Endpoints
@router.post("/session/start")
async def start_session(db: Session = Depends(get_db)):
    service = WhatsAppSessionService(db)
    result = await service.start_session()
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result.get("detail", result["error"]))
    return result

@router.post("/session/stop")
async def stop_session(db: Session = Depends(get_db)):
    service = WhatsAppSessionService(db)
    result = await service.stop_session()
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result.get("detail", result["error"]))
    return {"status": "success", "result": result}

def parse_duration(duration_str: str) -> timedelta:
    """Parse duration string like '4h' or '3h30' into timedelta."""
    match = re.match(r"(\d+)h(?:(\d+))?", duration_str)
    if not match:
        return timedelta(hours=2)  # Default
    hours = int(match.group(1))
    minutes = int(match.group(2)) if match.group(2) else 0
    return timedelta(hours=hours, minutes=minutes)

@router.post("/appointments", response_model=Appointment)
async def create_appointment(appointment_in: AppointmentCreate, db: Session = Depends(get_db)):
    # Check if hairstyle exists
    style = db.query(models.Hairstyle).filter(models.Hairstyle.id == appointment_in.style_id).first()
    if not style:
        raise HTTPException(status_code=404, detail="Hairstyle not found")
    
    # Calculate end time
    duration = parse_duration(style.duration)
    start_time = appointment_in.date
    end_time = start_time + duration
    
    # Check for overlaps
    # Overlap condition: (existing_start < requested_end) AND (existing_end > requested_start)
    # Note: We need to know the duration of existing appointments too.
    # To simplify, we'll join with Hairstyle or store end_time in DB.
    # Let's use a join to get existing durations.
    
    existing_appointments = db.query(models.Appointment, models.Hairstyle).\
        join(models.Hairstyle, models.Appointment.style_id == models.Hairstyle.id).\
        all()
    
    for appt, appt_style in existing_appointments:
        appt_duration = parse_duration(appt_style.duration)
        appt_end = appt.date + appt_duration
        
        if (appt.date < end_time) and (appt_end > start_time):
            raise HTTPException(
                status_code=400, 
                detail=f"Time slot already occupied by '{appt_style.name}' until {appt_end.strftime('%H:%M')}"
            )
    
    # Create appointment
    db_appointment = models.Appointment(**appointment_in.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    # Notify Admin if phone number is configured
    if ADMIN_PHONE_NUMBER:
        try:
            whatsapp_service = WhatsAppSessionService(db)
            msg = (
                f"🔔 *Nouvelle Réservation*\n"
                f"👤 Client: {db_appointment.customer_name}\n"
                f"💇 Prestation: {style.name}\n"
                f"📅 Date: {db_appointment.date.strftime('%d/%m/%Y à %H:%M')}\n"
                f"📞 Tel: {db_appointment.telephone}\n"
                f"🆔 ID: {db_appointment.id[:8]}"
            )
            # Use background tasks if needed for performance, keeping it simple for now
            import asyncio
            asyncio.create_task(whatsapp_service.send_message(
                chat_id=ADMIN_PHONE_NUMBER,
                text=msg
            ))
        except Exception as e:
            print(f"Failed to send admin notification: {e}")

    return db_appointment

@router.get("/appointments", response_model=List[Appointment])
async def list_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointment).all()


@router.post("/send")
async def send_whatsapp_message(
    msg_in: WhatsAppMessageSend, 
    db: Session = Depends(get_db)
):
    service = WhatsAppSessionService(db)
    result = await service.send_message(
        chat_id=msg_in.chat_id,
        text=msg_in.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
        
    return {"status": "success", "data": result}