# app/routes/predict.py
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.etl import transform_records
from app.services.ml_service import MLService
from app.services.alert_dispatcher import AlertDispatcher
from app.utils.security import verify_api_key
from app.db.timeseries import write_telemetry

router = APIRouter(prefix="/predict", tags=["predict"], dependencies=[Depends(verify_api_key)])

class Record(BaseModel):
    device_id: str
    ts: float
    value: float
    meta: Dict[str, Any] = {}

class PredictRequest(BaseModel):
    records: List[Record]

class Prediction(BaseModel):
    device_id: str
    ts: float
    p_fail: float
    meta: Dict[str, Any] = {}

@router.post("/", response_model=List[Prediction])
def predict(payload: PredictRequest):
    try:
        # write raw telemetry to DB (fire-and-forget semantics - errors logged inside)
        for r in payload.records:
            write_telemetry(r.dict())

        # ETL -> features
        features = transform_records([r.dict() for r in payload.records])

        # ML inference
        ml = MLService.get_instance()
        preds = ml.predict_batch(features)

        out = []
        for rec, p in zip(payload.records, preds):
            item = {"device_id": rec.device_id, "ts": rec.ts, "p_fail": float(p), "meta": rec.meta}
            out.append(item)
            # send alert if threshold exceeded (non-blocking)
            if float(p) > 0.5:
                AlertDispatcher.send_alert(item)
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
