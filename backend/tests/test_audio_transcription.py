import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import LLMService
from database import SessionLocal
import models

async def test_audio_transcription():
    load_dotenv()
    db = SessionLocal()
    llm_service = LLMService(db)
    
    # Path to the existing audio file found in the workspace
    audio_file = os.path.join(os.getcwd(), "node/audio_data/audio_41077318881307_2026-02-10T09-20-53-115Z.ogg")
    
    if not os.path.exists(audio_file):
        print(f"Error: Test audio file not found at {audio_file}")
        return

    print(f"--- Testing Transcription for {audio_file} ---")
    try:
        with open(audio_file, "rb") as f:
            audio_content = f.read()
            
        transcription = await llm_service.transcribe_audio(audio_content, os.path.basename(audio_file))
        print(f"TRANSCRIPTION: {transcription}")
        
        print("\n--- Testing Processing Transcribed Message ---")
        response = await llm_service.process_message(transcription, "test_user")
        print(f"AI RESPONSE: {response}")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_audio_transcription())
