from typing import List, Dict

def extract_whatsapp_user_messages(payload: dict) -> List[Dict]:
    """
    Extrait et normalise les messages envoyés par l'utilisateur
    depuis un webhook WhatsApp / WAWP.
    """

    messages_out = []

    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                for msg in value.get("messages", []):
                    msg_type = msg.get("type")

                    message_data = {
                        "from": msg.get("from"),
                        "type": msg_type,
                        "timestamp": msg.get("timestamp"),
                        "message_id": msg.get("id"),
                    }

                    if msg_type == "text":
                        message_data["text"] = msg["text"]["body"]

                    elif msg_type == "audio":
                        message_data["audio_id"] = msg["audio"]["id"]
                        message_data["mime_type"] = msg["audio"].get("mime_type")

                    elif msg_type == "image":
                        message_data["image_id"] = msg["image"]["id"]
                        message_data["mime_type"] = msg["image"].get("mime_type")

                    elif msg_type == "button":
                        message_data["text"] = msg["button"]["text"]

                    elif msg_type == "interactive":
                        message_data["interactive"] = msg["interactive"]

                    messages_out.append(message_data)

    except Exception as e:
        logger.exception("Error while parsing WhatsApp webhook payload")

    return messages_out
