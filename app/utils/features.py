# дополнительные утилиты для вычисления признаков
def compute_moving_avg(values, window=3):
    if not values:
        return 0.0
    window = max(1, window)
    return sum(values[-window:]) / min(len(values), window)
