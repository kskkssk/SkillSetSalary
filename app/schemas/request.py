from pydantic import BaseModel


class PdfPath(BaseModel):
    pdf_path: str

    class Config:
        from_attributes = True
