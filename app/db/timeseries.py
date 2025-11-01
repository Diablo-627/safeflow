# app/db/timeseries.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from .models import Base, Telemetry
import json
import logging

logger = logging.getLogger("timeseries")

# Simple synchronous engine for dev (sqlite by default)
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def write_telemetry(rec: dict):
    """Write a single telemetry record (safe: errors logged)."""
    try:
        s = SessionLocal()
        t = Telemetry(
            device_id=rec.get("device_id"),
            ts=rec.get("ts"),
            value=rec.get("value"),
            meta=json.dumps(rec.get("meta", {}))
        )
        s.add(t)
        s.commit()
    except Exception as e:
        logger.exception("Failed to write telemetry: %s", e)
    finally:
        try:
            s.close()
        except Exception:
            pass

def read_window(device_id: str, ts_from: float, ts_to: float):
    """Return telemetry rows for a device in a time window."""
    s = SessionLocal()
    try:
        q = s.query(Telemetry).filter(
            Telemetry.device_id == device_id,
            Telemetry.ts >= ts_from,
            Telemetry.ts <= ts_to
        ).order_by(Telemetry.ts)
        return [ {
            "device_id": r.device_id,
            "ts": r.ts,
            "value": r.value,
            "meta": r.meta
        } for r in q ]
    finally:
        s.close()
