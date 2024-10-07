from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from services.crud.user_service import UserService
from services.crud.person_service import PersonService
from database.database import get_db
from schemas.user import UserResponse
from typing import List


user_get_route = APIRouter(tags=['User'])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_person_service(user_service: UserService = Depends(get_user_service)) -> PersonService:
    current_user = user_service.get_current_user()
    return PersonService(user_service.session, current_user)


@user_get_route.get("/all", response_model=List[UserResponse])
async def get_all_users(user_service: UserService = Depends(get_user_service)):
    users = user_service.get_all_users()
    return [UserResponse.from_orm(user) for user in users]


@user_get_route.get("/user/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, user_service: UserService = Depends(get_user_service)):
    user = user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.from_orm(user)


@user_get_route.get("/user/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, user_service: UserService = Depends(get_user_service)):
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.from_orm(user)


@user_get_route.get("/transaction_history", response_model=List[dict])
async def transaction_history(person_service: PersonService = Depends(get_person_service)):
    return person_service.transaction_history()


@user_get_route.get("/current_user", response_model=UserResponse)
async def get_current_user(user_service: UserService = Depends(get_user_service)):
    user = user_service.get_current_user()
    return UserResponse.from_orm(user)