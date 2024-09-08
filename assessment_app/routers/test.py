from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from assessment_app.models.models import User, RegisterUserRequest
# from assessment_app.repository.database import get_db

router = APIRouter()


@router.get("/test", response_model=str)
async def test() -> str:
    """
    test
    """
    print("hiiiii")
    # with get_db() as db:
    #     print(db)
    return "hellooooo"

