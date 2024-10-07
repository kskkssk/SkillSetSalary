from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Dict
from models.balance import Balance
from models.user import User
from services.crud.balance_service import BalanceService
from services.crud.request_service import RequestService
from datetime import datetime, timezone


class PersonService:
    def __init__(self, session: Session, current_user: User):
        self.session = session
        self.current_user = current_user
        self.balance_service = BalanceService(session)
        self.request_service = RequestService(session)

    def handle_request(self, pdf_path: str):
        if self.current_user is None:
            raise ValueError("No user is currently logged in")

        time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        today = datetime.now().date()
        prediction = self.request_service.predict(pdf_path)
        requests = [trans for trans in self.current_user.transaction_list if
                    datetime.strptime(trans['current_time'], '%Y-%m-%d %H:%M:%S').date() == today
                    ]

        transaction_data = {
            'spent_money': 0,
            'salary': prediction,
            'current_time': time
        }
        if len(requests) < 2:
            self.current_user.transaction_list.append(transaction_data)
            flag_modified(self.current_user, "transaction_list")
            self.session.commit()
            return transaction_data
        else:
            print("Сделано уже два запроса сегодня")
            spent_sum = 0
            if self.balance_service.deduct_balance(user_id=self.current_user.id, amount=100):
                spent_sum += 100
                transaction_data['spent_money'] = spent_sum
                self.current_user.transaction_list.append(transaction_data)
                flag_modified(self.current_user, "transaction_list")
                self.session.commit()
                return transaction_data
            else:
                raise ValueError("Not enough balance")

    def handle_interpret(self, pdf_path: str):
        if self.current_user is None:
            raise ValueError("No user is currently logged in")
        skills_improve, skills_advice = self.request_service.interpretate_pred(pdf_path)
        return skills_improve, skills_advice

    def transaction_history(self) -> List[dict]:
        if self.current_user is None:
            raise ValueError("No user is currently logged in")
        return self.current_user.transaction_list

    def add_balance(self, amount: float) -> Balance:
        return self.balance_service.add_balance(self.current_user.id, amount)

    def get_balance(self) -> Balance:
        return self.balance_service.get_balance(self.current_user.id)

    def deduct_balance(self, amount: float) -> Balance:
        return self.balance_service.deduct_balance(self.current_user.id, amount)

    def get_requests_by_user(self) -> List[Dict]:
        return self.request_service.get_requests_by_user(self.current_user.id)
