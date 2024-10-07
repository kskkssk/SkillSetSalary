from database.database import SessionLocal
from services.crud.user_service import UserService
from services.crud.balance_service import BalanceService

if __name__ == "__main__":

    with SessionLocal() as session:
        user_service = UserService(session)
        balance_service = BalanceService(session)

