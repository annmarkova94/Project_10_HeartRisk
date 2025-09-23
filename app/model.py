import pandas as pd
import joblib

class HeartRiskModel:
    def __init__(self, path='model_with_threshold.pkl'):
        data = joblib.load(path)
        self.threshold = data['threshold']
        self.model = data['model']

    def predict_risk(self, X: pd.DataFrame) -> float:
        risk_prob = self.model.predict_proba(X)[:,1][0]
        risk_bool = risk_prob > self.threshold
        return {
            'threshold': self.threshold,
            'risk_prob': risk_prob,
            'risk_bool': risk_bool
        }
