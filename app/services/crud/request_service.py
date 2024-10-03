from catboost import CatBoostRegressor
import joblib
import shap
import pandas as pd
from app.schemas.request import SalaryPredictionResponse, ShapValuesResponse


class RequestService:
    def __init__(self, session):
        self.session = session

    def validate(self, pdf_path: str):
        try:
            pdf_path.endswith('.pdf')
            return pdf_path
        except ValueError:
            raise ValueError('Expected file in format: .pdf')

    def load_model(self) -> CatBoostRegressor:
        model_path = 'cb_super'
        with open(model_path, 'rb') as f:
            model = joblib.open(f)
        return model

    def prediction(self, data: pd.DataFrame) -> SalaryPredictionResponse:
        model = self.load_model()
        salary = model.predict(data)
        return SalaryPredictionResponse(salary=salary)

    def interpretate(self, data: pd.DataFrame) -> ShapValuesResponse:
        model = self.load_model()
        explainer = shap.Explainer(model)
        shap_values = explainer(data)
        shap_values_df = pd.DataFrame(shap_values.values, columns=data.columns)
        shap_values_dict = shap_values_df.to_dict(orient='list')
        return ShapValuesResponse(shap_values=shap_values_dict)


