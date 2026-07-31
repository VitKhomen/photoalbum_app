from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import ADMIN_USERNAME
from app.security import decode_access_token

# tokenUrl лише для документації Swagger (/docs) - реальний логін в admin-роутері
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")


def get_current_admin(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невірний або протермінований токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = decode_access_token(token)
    if username is None or username != ADMIN_USERNAME:
        raise credentials_exception

    return username
