import os
import models
from database import engine
from dotenv import load_dotenv

load_dotenv()

ADMIN_PHONE_NUMBER = os.getenv("ADMIN_PHONE_NUMBER")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# Initialize database
models.Base.metadata.create_all(bind=engine)
