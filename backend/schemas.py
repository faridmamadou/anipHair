from pydantic import BaseModel, ConfigDict, Field
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

class WhatsAppMessageSend(BaseModel):
    chat_id: str
    message: str

class WhatsAppMessage(BaseModel):
    chat_id: str
    message_type: str
    content: str

class WhatsAppMessageReceive(BaseModel):
    type: str
    message: Optional[str] = None
    sender_id: str

