# простая online feature transform: нормализация value + rolling placeholder
def transform_records(records):
    """
    records: list of dicts with keys device_id, ts, value, meta
    возвращает: list of feature dicts
    """
    out = []
    # простой min-max normalization с предположительными границами
    MIN_V, MAX_V = 0.0, 100.0
    for r in records:
        value = float(r.get("value", 0.0))
        value_norm = (value - MIN_V) / (MAX_V - MIN_V) if MAX_V > MIN_V else 0.0
        out.append({"device_id": r.get("device_id"), "ts": r.get("ts"), "value_norm": value_norm})
    return out
