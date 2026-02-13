import os
import sys
import asyncio
from datetime import datetime, timedelta

from dotenv import load_dotenv

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from database import SessionLocal
from services.messages_service import MessagesService
import models

async def test_llm_agent():
    db = SessionLocal()
    service = MessagesService(db)
    
    test_queries = [
        "Quels sont mes rendez-vous pour aujourd'hui ?",
        "Quelles sont les heures creuses pour demain ?",
        "Bloque un créneau pour Mariam pour Twists Passion demain à 14h.",
        "Liste les rendez-vous de demain.",
        "Annule le rendez-vous de Mariam."
    ]
    
    sender_id = "test_user"
    
    print("--- Starting LLM Agent Verification ---\n")
    
    for query in test_queries:
        print(f"USER: {query}")
        try:
            response = await service.process_message(query, sender_id)
            print(f"AGENT: {response}\n")
        except Exception as e:
            print(f"ERROR: {e}\n")
            
    db.close()

if __name__ == "__main__":
    asyncio.run(test_llm_agent())
