from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column
from database.database import Base


class Request(Base):
    __tablename__ = 'requests'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    model = mapped_column(String)
    user_id = mapped_column(Integer, ForeignKey('users.id'))
    pdf_path = mapped_column(String)
    
