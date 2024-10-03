from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.crud.user_service import UserService
from app.services.crud.personal_service import PersonService
from app.database.database import get_db

user_delete_route = APIRouter(tags=['User'])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_person_service(user_service: UserService = Depends(get_user_service)) -> PersonService:
    current_user = user_service.get_current_user()
    return PersonService(user_service.session, current_user)


@user_delete_route.delete("/user/{user_id}", response_model=dict)
async def delete_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    try:
        user_service.delete_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"message": "User deleted successfully"}