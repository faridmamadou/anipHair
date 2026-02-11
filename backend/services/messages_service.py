from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models
import logging

logger = logging.getLogger(__name__)

class MessagesService:
    def __init__(self, db: Session):
        self.db = db

    async def process_message(self, text: str, sender_id: str) -> str:
        content = text.strip().upper()
        
        if content == "LIST" or content == "TODAY":
            return await self._get_today_appointments()
        
        if content == "HELP":
            return "Guide Anip Hair :\n\n- LIST : Voir les RDV du jour\n- TODAY : Alias de LIST\n- HELP : Ce menu"

        # LLM Placeholder
        return await self._call_llm_placeholder(text)

    async def _get_today_appointments(self) -> str:
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        appts = (
            self.db.query(models.Appointment)
            .filter(models.Appointment.date >= start_of_day)
            .filter(models.Appointment.date < end_of_day)
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

    async def _call_llm_placeholder(self, text: str) -> str:
        # Ici, vous pourrez ajouter votre logique LLM plus tard
        # Pour l'instant on renvoie juste un accusé de réception
        return f"Message reçu ! (Le LLM n'est pas encore activé pour analyser : '{text}')"
