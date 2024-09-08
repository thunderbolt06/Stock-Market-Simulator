from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(request: Request) -> str:
    """
    Get jwt_token from request cookies from database and return corresponding user id which is `email_id` to keep it simple.
    Verify the jwt_token is authentic (from database) and is not expired.
    """
    jwt_token = request.cookies.get("jwt_token")
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    # TODO: Verify the jwt_token is authentic (from database) and is not expired.
    # For now, just return the token
    return jwt_token


def create_jwt_token(user_id, expiration_time):
    payload = {"user_id": user_id, "exp": expiration_time}
    secret_key = "RahilJain"
    return jwt.encode(payload, secret_key, algorithm="HS256")
