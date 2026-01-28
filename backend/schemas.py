from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

# Hairstyle Schemas
class HairstyleBase(BaseModel):
    name: str
    price: str
    duration: str
    image: str
    category: str

class Hairstyle(HairstyleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Appointment Schemas
class AppointmentBase(BaseModel):
    style_id: int
    customer_name: str
    telephone: str
    date: datetime
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: str
    created_at: datetime
    status: str
    model_config = ConfigDict(from_attributes=True)

# WhatsApp Session Schemas
class WhatsAppSessionBase(BaseModel):
    session_name: str
    status: str
    qr_code: Optional[str] = None

class WhatsAppSession(WhatsAppSessionBase):
    id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WhatsAppMessageSend(BaseModel):
    chat_id: str
    message: str

class WhatsAppMessage(BaseModel):
    chat_id: str
    message_type: str
    content: str
    received_at: datetime = datetime.utcnow()

class WhatsAppAudioMessage(BaseModel):
    chat_id: str
    message_type: str
    message_id: str
    audio_url: str  # URL directe du fichier audio
    mime_type: Optional[str] = None
    filename: Optional[str] = None
    s3_bucket: Optional[str] = None
    s3_key: Optional[str] = None
    from_number: str = Field(..., alias="from")
    to: Optional[str] = None
    timestamp: int
    fromMe: bool
    body: Optional[str] = None
    received_at: str

    class Config:
        populate_by_name = True