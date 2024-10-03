from pydantic import BaseModel
from typing import Dict, List


class PdfPath(BaseModel):
    pdf_path: str

    class Config:
        orm_mode = True
        from_attributes = True


class SalaryPredictionResponse(BaseModel):
    salary: float

    class Config:
        orm_mode = True
        from_attributes = True


class ShapValuesResponse(BaseModel):
    shap_values: Dict[str, List[float]]

    class Config:
        orm_mode = True
        from_attributes = True