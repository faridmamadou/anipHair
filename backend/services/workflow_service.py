from sqlalchemy.orm import Session
import models
import schemas
from services.whatsapp_service import WhatsAppSessionService
import os
import logging
from typing import Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class WorkflowService:
    def __init__(self, db: Session):
        self.db = db
        self.whatsapp_service = WhatsAppSessionService(db)
        self.admin_number = os.getenv("ADMIN_PHONE_NUMBER")

    async def handle_whatsapp_event(self, event: Dict[str, Any]):
        event_type = event.get("event")
        
        # Security: Only allow ADMIN_PHONE_NUMBER to interact with the agent
        payload = event.get("data", {})
        sender_raw = payload.get("from", "") # e.g. 229XXXXXXXX@c.us
        sender = sender_raw.split("@")[0] if sender_raw else ""
        
        if self.admin_number and sender != self.admin_number:
            logger.info(f"Ignoring message from unauthorized number: {sender}")
            return None

        if event_type == "message":
            return await self._handle_admin_command(event)
        elif event_type == "connection.update":
            return await self._handle_connection_update(event)
        
        return None

    async def _handle_admin_command(self, event: Dict[str, Any]):
        payload = event.get("data", {})
        message_obj = payload.get("message", {})
        content = (message_obj.get("conversation") or 
                   message_obj.get("extendedTextMessage", {}).get("text", "")).strip()
        
        chat_id = payload.get("from")
        instance = event.get("instanceName", "default")

        if not content:
            return None

        cmd = content.split()[0].upper()
        args = content.split()[1:]

        if cmd == "LIST":
            return await self._cmd_list(chat_id, instance)
        elif cmd == "CONFIRM":
            return await self._cmd_confirm(chat_id, instance, args)
        elif cmd == "CANCEL":
            return await self._cmd_cancel(chat_id, instance, args)
        elif cmd == "HELP":
            return await self._cmd_help(chat_id, instance)
        else:
            await self.whatsapp_service.send_message(
                chat_id=chat_id,
                text="❌ Commande inconnue. Tapez *HELP* pour voir la liste.",
                session_name=instance
            )
        
        return {"command": cmd, "processed": True}

    async def _cmd_list(self, chat_id: str, instance: str):
        # Get pending and confirmed appointments for today/future
        now = datetime.now()
        appts = self.db.query(models.Appointment).filter(
            models.Appointment.date >= now.replace(hour=0, minute=0, second=0)
        ).order_by(models.Appointment.date).all()

        if not appts:
            msg = "📭 Aucun rendez-vous prévu pour aujourd'hui."
        else:
            msg = "📅 *Planning Anip Hair*\n\n"
            for a in appts:
                status_icon = "⏳" if a.status == "pending" else "✅"
                msg += f"{status_icon} `{a.id[:8]}` - {a.date.strftime('%H:%M')} | {a.customer_name} ({a.style.name})\n"
            
            msg += "\n💡 Utilisez `CONFIRM [ID]` ou `CANCEL [ID]`"

        await self.whatsapp_service.send_message(chat_id=chat_id, text=msg, session_name=instance)

    async def _cmd_confirm(self, chat_id: str, instance: str, args: list):
        if not args:
            await self.whatsapp_service.send_message(chat_id=chat_id, text="⚠️ Précisez l'ID. Ex: `CONFIRM ab12cd34`", session_name=instance)
            return

        appt_id_partial = args[0]
        appt = self.db.query(models.Appointment).filter(models.Appointment.id.like(f"{appt_id_partial}%")).first()
        
        if not appt:
            msg = f"❌ Rendez-vous `{appt_id_partial}` introuvable."
        else:
            appt.status = "confirmed"
            self.db.commit()
            msg = f"✅ RDV de {appt.customer_name} ({appt.id[:8]}) CONFIRMÉ."

        await self.whatsapp_service.send_message(chat_id=chat_id, text=msg, session_name=instance)

    async def _cmd_cancel(self, chat_id: str, instance: str, args: list):
        if not args:
            await self.whatsapp_service.send_message(chat_id=chat_id, text="⚠️ Précisez l'ID. Ex: `CANCEL ab12cd34`", session_name=instance)
            return

        appt_id_partial = args[0]
        appt = self.db.query(models.Appointment).filter(models.Appointment.id.like(f"{appt_id_partial}%")).first()
        
        if not appt:
            msg = f"❌ Rendez-vous `{appt_id_partial}` introuvable."
        else:
            appt.status = "canceled"
            self.db.commit()
            msg = f"🗑️ RDV de {appt.customer_name} ({appt.id[:8]}) ANNULÉ."

        await self.whatsapp_service.send_message(chat_id=chat_id, text=msg, session_name=instance)

    async def _cmd_help(self, chat_id: str, instance: str):
        msg = (
            "🤖 *Guide de l'Agent Anip Hair*\n\n"
            "• *LIST* : Voir les rendez-vous du jour\n"
            "• *CONFIRM [ID]* : Valider un RDV\n"
            "• *CANCEL [ID]* : Annuler un RDV\n"
            "• *HELP* : Afficher ce guide"
        )
        await self.whatsapp_service.send_message(chat_id=chat_id, text=msg, session_name=instance)

    async def _handle_connection_update(self, event: Dict[str, Any]):
        payload = event.get("data", {})
        instance_name = event.get("instanceName")
        status = payload.get("status") # e.g. "open", "close", "connecting"
        
        db_session = self.db.query(models.WhatsAppSession).filter(models.WhatsAppSession.session_name == instance_name).first()
        if db_session:
            if status == "open":
                db_session.status = "CONNECTED"
            elif status == "close":
                db_session.status = "DISCONNECTED"
            elif status == "connecting":
                db_session.status = "CONNECTING"
            
            self.db.commit()
            logger.info(f"Updated session {instance_name} status to {db_session.status}")

    async def _handle_message_ack(self, event: Dict[str, Any]):
        # Tracking delivery if needed
        pass
