from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    ts = Column(Float, index=True)
    value = Column(Float)
    meta = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
