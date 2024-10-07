from sqlalchemy import Integer, Float, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from database.database import Base


class Balance(Base):
    __tablename__ = 'balance'
    __table_args__ = {'extend_existing': True}
    id = mapped_column(Integer, primary_key=True)
    amount = mapped_column(Float, default=0.0)
    user_id = mapped_column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="balance")
