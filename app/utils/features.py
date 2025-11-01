# app/utils/features.py
from typing import List

def rolling_mean(values: List[float], window: int = 3) -> float:
    if not values:
        return 0.0
    window = max(1, window)
    return sum(values[-window:]) / min(len(values), window)
