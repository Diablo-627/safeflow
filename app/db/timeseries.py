from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from .models import Base, Telemetry

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def write_record(rec: dict):
    s = SessionLocal()
    try:
        t = Telemetry(device_id=rec["device_id"], ts=rec["ts"], value=rec["value"], meta=str(rec.get("meta", {})))
        s.add(t)
        s.commit()
    finally:
        s.close()
