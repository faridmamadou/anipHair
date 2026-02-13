import io
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from groq import Groq

import models
import schemas
from database import SessionLocal

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, db: Session):
        self.db = db
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.whisper_model = "whisper-large-v3-turbo"

    async def transcribe_audio(self, audio_content: bytes, filename: str) -> str:
        """Transcribe audio content (bytes) using Groq Whisper."""
        try:
            logger.info(f"Transcribing audio: {filename} ({len(audio_content)} bytes)")
            
            # Wrap bytes in a file-like object for Groq
            audio_file = io.BytesIO(audio_content)
            audio_file.name = filename
            
            transcription = self.client.audio.transcriptions.create(
                file=audio_file,
                model=self.whisper_model,
                response_format="text",
                language="fr"  # Assuming predominantly French
            )
            
            logger.info(f"Transcription result: {transcription}")
            return str(transcription).strip()

        except Exception as e:
            logger.error(f"Error in LLM transcribe_audio: {e}")
            raise e

    async def process_message(self, text: str, sender_id: str) -> str:
        """Process a message using GROQ LLM and function calling."""
        
        # Fetch hairstyles for context
        styles = self.db.query(models.Hairstyle).all()
        style_names = ", ".join([s.name for s in styles])

        system_prompt = (
            "Tu es l'assistant de gestion d'Anip Hair. "
            f"Date du jour : {datetime.now().strftime('%Y-%m-%d')}. "
            "Catalogue : " + style_names + ". "
            "Utilise les outils pour répondre aux demandes."
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_appointments",
                    "description": "Liste les rendez-vous d'une journée.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Date au format YYYY-MM-DD"
                            }
                        },
                        "required": ["date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_free_slots",
                    "description": "Trouve les créneaux libres d'une journée.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Date au format YYYY-MM-DD"
                            }
                        },
                        "required": ["date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "block_time_slot",
                    "description": "Bloque un créneau horaire.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_name": {"type": "string"},
                            "style_name": {"type": "string"},
                            "date_time": {"type": "string", "description": "YYYY-MM-DD HH:MM"}
                        },
                        "required": ["customer_name", "style_name", "date_time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cancel_appointment",
                    "description": "Annule un rendez-vous.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "appointment_id": {"type": "string", "description": "ID ou partie de l'ID"},
                            "customer_name": {"type": "string"}
                        },
                        "required": []
                    }
                }
            }
        ]

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        functions_map = {
            "list_appointments": self._tool_list_appointments,
            "list_free_slots": self._tool_list_free_slots,
            "block_time_slot": self._tool_block_time_slot,
            "cancel_appointment": self._tool_cancel_appointment,
        }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                # Add the assistant's message with tool calls to history
                messages.append(response_message)
                
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"LLM calling function: {tool_name} with args: {tool_args}")
                    
                    # Execute the tool
                    if tool_name in functions_map:
                        result = await functions_map[tool_name](**tool_args)
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps(result) if not isinstance(result, str) else result
                        })
                
                # Get the final response from the model
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
                return second_response.choices[0].message.content
            
            return response_message.content

        except Exception as e:
            logger.error(f"Error in LLM process_message: {e}")
            return f"Désolé, j'ai rencontré une erreur technique : {str(e)}"

    # Suppression de la méthode _execute_tool devenue inutile car on utilise functions_map

    async def _tool_list_appointments(self, date: Optional[str] = None) -> str:
        if not date:
            date_dt = datetime.now()
        else:
            try:
                date_dt = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return "Format de date invalide. Utilisez YYYY-MM-DD."

        start_of_day = date_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        appts = (
            self.db.query(models.Appointment)
            .filter(models.Appointment.date >= start_of_day)
            .filter(models.Appointment.date < end_of_day)
            .filter(models.Appointment.status != "canceled")
            .order_by(models.Appointment.date)
            .all()
        )

        if not appts:
            return f"Aucun rendez-vous prévu pour le {date_dt.strftime('%d/%m/%Y')}."

        msg = f"Rendez-vous pour le {date_dt.strftime('%d/%m/%Y')} :\n"
        for a in appts:
            time_str = a.date.strftime('%H:%M')
            msg += f"- {time_str} : {a.customer_name} ({a.style.name if a.style else 'N/A'}) [ID: {a.id[:8]}]\n"
        
        return msg

    async def _tool_list_free_slots(self, date: Optional[str] = None) -> str:
        if not date:
            date_dt = datetime.now()
        else:
            try:
                date_dt = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return "Format de date invalide. Utilisez YYYY-MM-DD."

        # Heures d'ouverture: 09h00 - 18h00
        opening_time = date_dt.replace(hour=9, minute=0, second=0, microsecond=0)
        closing_time = date_dt.replace(hour=18, minute=0, second=0, microsecond=0)

        # Chercher tous les appts du jour
        start_of_day = date_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        appts = (
            self.db.query(models.Appointment)
            .filter(models.Appointment.date >= start_of_day)
            .filter(models.Appointment.date < end_of_day)
            .filter(models.Appointment.status != "canceled")
            .all()
        )

        # Liste des créneaux occupés
        occupied_periods = []
        for a in appts:
            start = a.date
            # Durée par défaut 2h si non précisé
            duration_str = a.style.duration if a.style else "2h"
            duration = self._parse_duration(duration_str)
            end = start + duration
            occupied_periods.append((start, end))

        # Trouver les créneaux libres (simples créneaux de 1h pour simplifier la vue)
        free_slots = []
        current = opening_time
        while current < closing_time:
            next_hour = current + timedelta(hours=1)
            is_occupied = False
            for start, end in occupied_periods:
                if (current < end) and (next_hour > start):
                    is_occupied = True
                    break
            
            if not is_occupied:
                free_slots.append(current.strftime('%H:%M'))
            
            current = next_hour

        if not free_slots:
            return f"Aucun créneau libre disponible pour le {date_dt.strftime('%d/%m/%Y')}."

        return f"Créneaux libres pour le {date_dt.strftime('%d/%m/%Y')} : " + ", ".join(free_slots)

    async def _tool_block_time_slot(self, customer_name: str, style_name: str, date_time: str) -> str:
        try:
            date_time_dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        except ValueError:
            return "Format date_time invalide. Utilisez YYYY-MM-DD HH:MM."

        # Chercher le hairstyle par nom (fuzzy search simple)
        style = self.db.query(models.Hairstyle).filter(models.Hairstyle.name.ilike(f"%{style_name}%")).first()
        if not style:
            # Créer un style temporaire ou renvoyer erreur ? Renvoyons erreur pour l'instant
            return f"Prestation '{style_name}' non trouvée dans le catalogue. Veuillez préciser une prestation valide."

        # Vérifier si le créneau est libre
        duration = self._parse_duration(style.duration)
        end_time = date_time_dt + duration

        overlapping = (
            self.db.query(models.Appointment)
            .filter(models.Appointment.status != "canceled")
            .filter(models.Appointment.date < end_time)
            .all()
        )
        
        for a in overlapping:
            appt_start = a.date
            appt_duration = self._parse_duration(a.style.duration if a.style else "2h")
            appt_end = appt_start + appt_duration
            if (date_time_dt < appt_end) and (end_time > appt_start):
                return f"Conflit de planning : un rendez-vous ({a.customer_name}) est déjà prévu de {appt_start.strftime('%H:%M')} à {appt_end.strftime('%H:%M')}."

        # Créer le RDV
        new_appt = models.Appointment(
            style_id=style.id,
            customer_name=customer_name,
            telephone="Unknown", # À améliorer si possible
            date=date_time_dt,
            status="confirmed"
        )
        self.db.add(new_appt)
        self.db.commit()
        self.db.refresh(new_appt)

        return f"Rendez-vous confirmé pour {customer_name} ({style.name}) le {date_time_dt.strftime('%d/%m/%Y à %H:%M')}. [ID: {new_appt.id[:8]}]"

    async def _tool_cancel_appointment(self, appointment_id: Optional[str] = None, customer_name: Optional[str] = None) -> str:
        query = self.db.query(models.Appointment).filter(models.Appointment.status != "canceled")
        
        if appointment_id:
            appt = query.filter(models.Appointment.id.like(f"{appointment_id}%")).first()
        elif customer_name:
            appt = query.filter(models.Appointment.customer_name.ilike(f"%{customer_name}%")).order_by(models.Appointment.date.desc()).first()
        else:
            return "Veuillez fournir un ID de rendez-vous ou un nom de client."

        if not appt:
            return "Rendez-vous introuvable."

        appt.status = "canceled"
        self.db.commit()

        return f"Le rendez-vous de {appt.customer_name} le {appt.date.strftime('%d/%m/%Y à %H:%M')} a été annulé avec succès."

    def _parse_duration(self, duration_str: str) -> timedelta:
        """Parse duration string like '4h' or '3h30' into timedelta."""
        import re
        match = re.match(r"(\d+)h(?:(\d+))?", duration_str)
        if not match:
            return timedelta(hours=2)  # Default
        hours = int(match.group(1))
        minutes = int(match.group(2)) if match.group(2) else 0
        return timedelta(hours=hours, minutes=minutes)
