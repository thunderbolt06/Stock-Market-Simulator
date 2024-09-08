import datetime
import hashlib
import secrets
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from assessment_app.models.models import User, RegisterUserRequest
from assessment_app.models.schema import UserCredentials
from assessment_app.service.auth_service import create_jwt_token

router = APIRouter()


@router.post("/register", response_model=User)
async def register_user(user: RegisterUserRequest) -> User:
    """
    Register a new user in database and save the login details (email_id and password) separately from User.
    Also, do necessary checks as per your knowledge.
    """

    # Check if the email_id already exists in database
    existing_user = await User.get_by_email_id(user.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email id already exists")

    # Generate a random salt and hash the password
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((user.password + salt).encode()).hexdigest()

    # Create a new User and UserCredentials
    new_user = User(email=user.email, first_name=user.first_name, last_name=user.last_name)
    new_user_credentials = UserCredentials(user_id=new_user.id, password_hash=password_hash, random_salt=salt)

    # Save both to database
    await new_user.save()
    await new_user_credentials.save()

    return new_user


@router.post("/login", response_model=str)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()) -> JSONResponse:
    """
    Login user after verification of credentials and add jwt_token in response cookies.
    Also, do necessary checks as per your knowledge.
    """

    # Get UserCredentials object for the given email
    user_credentials = await UserCredentials.get_by_email_id(form_data.username)

    if not user_credentials:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Check if the password matches
    password_hash = hashlib.sha256((form_data.password + user_credentials.random_salt).encode()).hexdigest()

    if password_hash != user_credentials.password_hash:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate a jwt_token with the user_id and its expiration time
    jwt_token = create_jwt_token(user_id=user_credentials.email, expiration_time=datetime.utcnow() + datetime.timedelta(minutes=30))

    # Save the jwt_token to databse 
    user_credentials.jwt_token = jwt_token
    await user_credentials.save()

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="jwt_token", value=f"Bearer {jwt_token}", httponly=True
    )
    return response


@router.get("/logout")
async def logout_user() -> JSONResponse:
    """
    Logout user and remove jwt_token from response cookies.
    """

    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie(key="jwt_token")
    return response
