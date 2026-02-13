from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import re
from typing import List
from contextlib import asynccontextmanager
import models
import schemas
from database import SessionLocal, engine, get_db
from initial_data import HAIRSTYLES_SEED
from routers import whatsapp_router, messages_router
import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed database
    db = SessionLocal()
    try:
        if db.query(models.Hairstyle).count() == 0:
            for style_data in HAIRSTYLES_SEED:
                db_style = models.Hairstyle(**style_data)
                db.add(db_style)
            db.commit()
    finally:
        db.close()
    yield
    # Shutdown logic (if any) could go here

app = FastAPI(title="Anip Hair API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Simplified for dev, adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(whatsapp_router.router)
app.include_router(messages_router.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Anip Hair Backend is running with SQLite persistence"}

@app.get("/hairstyles", response_model=List[schemas.Hairstyle])
async def get_hairstyles(db: Session = Depends(get_db)):
    return db.query(models.Hairstyle).all()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
