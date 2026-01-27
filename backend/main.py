from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import re
from typing import List
from contextlib import asynccontextmanager
import models
import schemas
from database import SessionLocal, engine, get_db
from initial_data import HAIRSTYLES_SEED
from routers import webhooks
from services.whatsapp_service import WhatsAppSessionService
import os

ADMIN_PHONE_NUMBER = os.getenv("ADMIN_PHONE_NUMBER")
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed database
    db = SessionLocal()
    try:
        if db.query(models.Hairstyle).count() == 0:
            for style_data in HAIRSTYLES_SEED:
                db_style = models.Hairstyle(**style_data)
                db.add(db_style)
            db.commit()
    finally:
        db.close()
    yield
    # Shutdown logic (if any) could go here

app = FastAPI(title="Anip Hair API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhooks.router)

def parse_duration(duration_str: str) -> timedelta:
    """Parse duration string like '4h' or '3h30' into timedelta."""
    match = re.match(r"(\d+)h(?:(\d+))?", duration_str)
    if not match:
        return timedelta(hours=2)  # Default
    hours = int(match.group(1))
    minutes = int(match.group(2)) if match.group(2) else 0
    return timedelta(hours=hours, minutes=minutes)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Anip Hair Backend is running with SQLite persistence"}

@app.get("/hairstyles", response_model=List[schemas.Hairstyle])
async def get_hairstyles(db: Session = Depends(get_db)):
    return db.query(models.Hairstyle).all()

@app.post("/appointments", response_model=schemas.Appointment)
async def create_appointment(appointment_in: schemas.AppointmentCreate, db: Session = Depends(get_db)):
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

@app.get("/appointments", response_model=List[schemas.Appointment])
async def list_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointment).all()

# WhatsApp Management Endpoints
@app.post("/whatsapp/sessions", response_model=schemas.WhatsAppSession)
async def create_session(session_name: str, db: Session = Depends(get_db)):
    service = WhatsAppSessionService(db)
    return await service.create_session(session_name)

@app.post("/whatsapp/sessions/{session_name}/start")
async def start_session(session_name: str, db: Session = Depends(get_db)):
    service = WhatsAppSessionService(db)
    return await service.start_session(session_name)

@app.get("/whatsapp/sessions/{session_name}/status", response_model=schemas.WhatsAppSession)
async def get_session_status(session_name: str, db: Session = Depends(get_db)):
    service = WhatsAppSessionService(db)
    session = await service.get_session_status(session_name)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.post("/whatsapp/sessions/{session_name}/stop")
async def stop_session(session_name: str, db: Session = Depends(get_db)):
    service = WhatsAppSessionService(db)
    success = await service.stop_session(session_name)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to stop session")
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
