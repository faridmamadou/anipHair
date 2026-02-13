from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models
import logging
from services.llm_service import LLMService

logger = logging.getLogger(__name__)

class MessagesService:
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService(db)

    async def process_message(self, text: str, sender_id: str) -> str:
        content = text.strip().upper()
        
        if content == "TODAY":
            return await self._get_today_appointments()
        
        if content == "LIST":
            return await self._get_coming_appointments()
        
        if content == "HELP":
            return (
                "Guide Anip Hair :\n\n"
                "- TODAY : Voir les RDV du jour\n"
                "- LIST : Voir les RDV des 7 prochains jours\n"
                "- HELP : Ce menu\n\n"
                "Ou parlez-moi normalement ! Je peux :\n"
                "- Lister les rdv d'un jour précis\n"
                "- Trouver les heures creuses\n"
                "- Bloquer un créneau (ex: Marie pour Tresses demain à 10h)\n"
                "- Annuler un rendez-vous"
            )

        # Utilisation du LLM pour les requêtes en langage naturel
        return await self.llm_service.process_message(text, sender_id)

    async def process_audio_message(self, audio_content: bytes, filename: str, sender_id: str) -> str:
        """Transcribe audio and process the resulting text."""
        try:
            transcription = await self.llm_service.transcribe_audio(audio_content, filename)
            if not transcription or transcription.strip() == "":
                return "Je n'ai pas pu comprendre votre message audio. Pourriez-vous répéter ?"
            
            logger.info(f"Transcribed text: {transcription}")
            response = await self.process_message(transcription, sender_id)
            return f"🎤 *Transcription :* {transcription}\n\n{response}"
        except Exception as e:
            logger.error(f"Error in process_audio_message: {e}")
            return "Une erreur est survenue lors du traitement de votre message audio."

    async def _get_today_appointments(self) -> str:
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
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
            return "Aucun rendez-vous prévu pour aujourd'hui."

        msg = f"📅 Planning du {now.strftime('%d/%m/%Y')}\n\n"
        for a in appts:
            time_str = a.date.strftime('%H:%M')
            status_icon = "✅" if a.status == "confirmed" else "⏳"
            msg += f"{status_icon} {time_str} - {a.customer_name} ({a.style.name if a.style else 'N/A'})\n"
        
        return msg

    async def _get_coming_appointments(self) -> str:
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=7)

        appts = (
            self.db.query(models.Appointment)
            .filter(models.Appointment.date >= start_of_day)
            .filter(models.Appointment.date < end_of_day)
            .filter(models.Appointment.status != "canceled")
            .order_by(models.Appointment.date)
            .all()
        )

        if not appts:
            return "Aucun rendez-vous prévu pour les prochains jours."

        msg = "📅 Planning des prochains jours\n\n"
        for a in appts:
            time_str = a.date.strftime('%d/%m/%Y %H:%M')
            status_icon = "✅" if a.status == "confirmed" else "⏳"
            msg += f"{status_icon} {time_str} - {a.customer_name} ({a.style.name if a.style else 'N/A'})\n"
        
        return msg
