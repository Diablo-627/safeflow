from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.ml_service import MLService
from app.services.etl import transform_records
from app.services.alert_dispatcher import AlertDispatcher

router = APIRouter()

class Record(BaseModel):
    device_id: str
    ts: float
    value: float
    meta: dict = {}

class PredictRequest(BaseModel):
    records: List[Record]

class Prediction(BaseModel):
    device_id: str
    ts: float
    p_fail: float
    meta: dict = {}

@router.post("/", response_model=List[Prediction])
def predict(payload: PredictRequest):
    # 1) ETL -> feature matrix
    features = transform_records([r.dict() for r in payload.records])
    # 2) Inference
    ml = MLService.get_instance()
    preds = ml.predict_batch(features)  # возвращает list of floats
    # 3) Формируем ответ и при необходимости шлём alert
    out = []
    for rec, p in zip(payload.records, preds):
        out_rec = {"device_id": rec.device_id, "ts": rec.ts, "p_fail": float(p), "meta": rec.meta}
        out.append(out_rec)
        if p > 0.5:  # простое правило: p_fail > 0.5 -> alert
            AlertDispatcher.send_alert(out_rec)
    return out
