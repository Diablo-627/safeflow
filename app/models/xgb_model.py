# wrapper для реальной модели: сейчас заглушка
class XGBModelWrapper:
    def __init__(self, path):
        self.path = path
        self._loaded = False

    def load(self):
        self._loaded = True

    def predict(self, features):
        # features: list of dicts
        return [0.1 for _ in features]
