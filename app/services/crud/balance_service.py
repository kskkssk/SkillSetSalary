from sqlalchemy.orm import Session
from models.balance import Balance


class BalanceService:
    def __init__(self, session: Session):
        self.session = session

    def add_balance(self, user_id: int, amount: float) -> Balance:
        balance = self.session.query(Balance).filter_by(user_id=user_id).first()
        if balance:
            balance.amount += amount
        else:
            balance = Balance(user_id=user_id, amount=amount)
            self.session.add(balance)
        self.session.commit()
        return balance

    def get_balance(self, user_id: int) -> Balance:
        balance = self.session.query(Balance).filter_by(user_id=user_id).first()
        if balance:
            return balance
        else:
            raise ValueError(f"Balance for user {user_id} not found")

    def deduct_balance(self, user_id: int, amount: float) -> Balance:
        balance = self.get_balance(user_id)
        if amount <= balance.amount:
            balance.amount -= amount
            self.session.commit()
            return balance
        else:
            raise ValueError(f"Not enough balance for user {user_id}")
