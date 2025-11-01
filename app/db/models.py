# app/db/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    ts = Column(Float, index=True, nullable=False)
    value = Column(Float, nullable=False)
    meta = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
class PredictionRecord(Base):
    __tablename__ = "prediction_records"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    ts = Column(Float, index=True, nullable=False)
    p_fail = Column(Float, nullable=False)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
