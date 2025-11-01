# app/services/etl.py
from typing import List, Dict

def transform_records(records: List[Dict]) -> List[Dict]:
    """
    Minimal online feature transform:
      - min-max normalize value (assume 0..100)
      - placeholder for rolling avg / delta (to be expanded)
    """
    MIN_V, MAX_V = 0.0, 100.0
    out = []
    for r in records:
        value = float(r.get("value", 0.0))
        value_norm = (value - MIN_V) / (MAX_V - MIN_V) if MAX_V > MIN_V else 0.0
        # add other features placeholders
        out.append({
            "device_id": r.get("device_id"),
            "ts": r.get("ts"),
            "value_norm": value_norm,
            # future features: rolling_avg, delta, last_value ...
        })
    return out
