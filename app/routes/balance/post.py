from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from schemas.balance import BalanceResponse
from services.crud.person_service import PersonService
from services.crud.user_service import UserService
from database.database import get_db


balance_post_route = APIRouter(tags=['Balance'])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_person_service(user_service: UserService = Depends(get_user_service)) -> PersonService:
    current_user = user_service.get_current_user()
    return PersonService(user_service.session, current_user)


@balance_post_route.post("/add_balance", response_model=BalanceResponse)
async def add_balance(amount: float = Form(...), person_service: PersonService = Depends(get_person_service)):
    try:
        new_balance = person_service.add_balance(amount)
        return BalanceResponse(id=new_balance.user_id, amount=new_balance.amount)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))