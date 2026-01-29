import os
import models
from database import engine
from dotenv import load_dotenv

load_dotenv()

ADMIN_PHONE_NUMBER = os.getenv("ADMIN_PHONE_NUMBER")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
WAWP_BASE_URL = os.getenv("WAWP_BASE_URL")
WAWP_ACCESS_TOKEN = os.getenv("WAWP_ACCESS_TOKEN")
WAWP_API_INSTANCE = os.getenv("WAWP_API_INSTANCE")
# Initialize database
models.Base.metadata.create_all(bind=engine)
