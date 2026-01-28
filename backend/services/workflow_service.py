from sqlalchemy.orm import Session
import models
from services.whatsapp_service import WhatsAppSessionService
from config import ADMIN_PHONE_NUMBER
import os
import logging
from typing import Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkflowService:
    def __init__(self, db: Session):
        self.db = db
        self.whatsapp_service = WhatsAppSessionService(db)
        self.admin_number = ADMIN_PHONE_NUMBER

    async def handle_whatsapp_event(self, event: Dict[str, Any]):
        payload = event.get("data", {})
        parsed = self.whatsapp_service.parse_incoming_message(payload)

        if not parsed:
            return None

        sender_raw = parsed.get("from", "")
        sender = sender_raw.split("@")[0] if sender_raw else ""

        if self.admin_number and sender != self.admin_number:
            logger.info(f"Ignoring unauthorized sender {sender}")
            return None

        if parsed["type"] == "text":
            return await self._handle_text_command(
                chat_id=sender_raw,
                text=parsed["content"]
            )

        return None

    async def _handle_text_command(self, chat_id: str, text: str):
        content = text.strip()
        if not content:
            return None

        cmd, *args = content.split()
        cmd = cmd.upper()

        if cmd == "LIST":
            await self._cmd_list(chat_id)

        elif cmd == "CONFIRM":
            await self._cmd_confirm(chat_id, args)

        elif cmd == "CANCEL":
            await self._cmd_cancel(chat_id, args)

        elif cmd == "HELP":
            await self._cmd_help(chat_id)

        else:
            await self.whatsapp_service.send_message(
                chat_id=chat_id,
                text="Commande inconnue. Tapez HELP pour voir la liste."
            )

    async def _cmd_list(self, chat_id: str):
        now = datetime.now()
        appts = (
            self.db.query(models.Appointment)
            .filter(models.Appointment.date >= now.replace(hour=0, minute=0, second=0))
            .order_by(models.Appointment.date)
            .all()
        )

        if not appts:
            msg = "Aucun rendez-vous prevu pour aujourd'hui."
        else:
            msg = "Planning Anip Hair\n\n"
            for a in appts:
                status = "PENDING" if a.status == "pending" else "CONFIRMED"
                msg += (
                    f"[{status}] {a.id[:8]} - "
                    f"{a.date.strftime('%H:%M')} | "
                    f"{a.customer_name} ({a.style.name})\n"
                )

            msg += "\nUtilisez CONFIRM [ID] ou CANCEL [ID]"

        await self.whatsapp_service.send_message(chat_id=chat_id, text=msg)

    async def _cmd_confirm(self, chat_id: str, args: list):
        if not args:
            await self.whatsapp_service.send_message(
                chat_id=chat_id,
                text="Precisez l'ID. Exemple: CONFIRM ab12cd34"
            )
            return

        appt = (
            self.db.query(models.Appointment)
            .filter(models.Appointment.id.like(f"{args[0]}%"))
            .first()
        )

        if not appt:
            msg = f"Rendez-vous {args[0]} introuvable."
        else:
            appt.status = "confirmed"
            self.db.commit()
            msg = f"RDV de {appt.customer_name} ({appt.id[:8]}) confirme."

        await self.whatsapp_service.send_message(chat_id=chat_id, text=msg)

    async def _cmd_cancel(self, chat_id: str, args: list):
        if not args:
            await self.whatsapp_service.send_message(
                chat_id=chat_id,
                text="Precisez l'ID. Exemple: CANCEL ab12cd34"
            )
            return

        appt = (
            self.db.query(models.Appointment)
            .filter(models.Appointment.id.like(f"{args[0]}%"))
            .first()
        )

        if not appt:
            msg = f"Rendez-vous {args[0]} introuvable."
        else:
            appt.status = "canceled"
            self.db.commit()
            msg = f"RDV de {appt.customer_name} ({appt.id[:8]}) annule."

        await self.whatsapp_service.send_message(chat_id=chat_id, text=msg)

    async def _cmd_help(self, chat_id: str):
        msg = (
            "Guide de l'Agent Anip Hair\n\n"
            "LIST : Voir les rendez-vous du jour\n"
            "CONFIRM [ID] : Valider un rendez-vous\n"
            "CANCEL [ID] : Annuler un rendez-vous\n"
            "HELP : Afficher ce guide"
        )

        await self.whatsapp_service.send_message(chat_id=chat_id, text=msg)
