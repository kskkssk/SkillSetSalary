from sqlalchemy import Integer, Float, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from database.database import Base


class Balance(Base):
    __tablename__ = 'balance'
    id = mapped_column(Integer, primary_key=True)
    amount = mapped_column(Float, default=0.0)
    user_id = mapped_column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="balance")
