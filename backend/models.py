from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base

class Hairstyle(Base):
    __tablename__ = "hairstyles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(String)
    duration = Column(String)
    image = Column(String)
    category = Column(String)

    appointments = relationship("Appointment", back_populates="style")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    style_id = Column(Integer, ForeignKey("hairstyles.id"))
    customer_name = Column(String)
    telephone = Column(String)
    date = Column(DateTime)
    notes = Column(Text, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now)

    style = relationship("Hairstyle", back_populates="appointments")

class WhatsAppSession(Base):
    __tablename__ = "whatsapp_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String, unique=True, index=True)
    status = Column(String, default="DISCONNECTED") # DISCONNECTED, CONNECTING, CONNECTED
    qr_code = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
