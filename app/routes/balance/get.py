from fastapi import HTTPException
from schemas.balance import BalanceResponse
from fastapi import APIRouter, Depends
from services.crud.personal_service import PersonService
from services.crud.user_service import UserService
from database.database import get_db
from sqlalchemy.orm import Session


balance_get_route = APIRouter(tags=['Balance'])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_person_service(user_service: UserService = Depends(get_user_service)) -> PersonService:
    current_user = user_service.get_current_user()
    return PersonService(user_service.session, current_user)


@balance_get_route.get("/balance", response_model=BalanceResponse)
async def get_balance(person_service: PersonService = Depends(get_person_service)):
    try:
        balance = person_service.get_balance()
        return BalanceResponse(id=balance.user_id, amount=balance.amount)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))