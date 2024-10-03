from sqlalchemy import Integer, String, JSON
from sqlalchemy.orm import mapped_column, relationship
from database.database import Base


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = mapped_column(Integer, primary_key=True)
    password = mapped_column(String, nullable=False)
    email = mapped_column(String, unique=True, nullable=False)

    balance = relationship('Balance', uselist=False, back_populates='user')
    transaction_list = mapped_column(JSON, default=list, nullable=False)