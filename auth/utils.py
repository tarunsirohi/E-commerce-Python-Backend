from datetime import datetime, timedelta, timezone  # used for the expiration time for JWT
from jose import JWTError, jwt  # used for creating and decoding JWTs and for handling potential errors during decoding.
from passlib.context import CryptContext  # for hashing and verifying passwords
from fastapi import Depends, HTTPException, status  # dependency inject system to manage sessions.
from fastapi.security import OAuth2PasswordBearer  # class that provides a dependency to extract the token from the request's authorization header.
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Creating instance of cyrptcontext and also, depcrecated is used if any older hashing shcmes were used passlib would automatically upgrade them to bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Create a reusable hasher instance
ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
SECRET_KEY = "secret_key_h"
# cryptographic algo to use for signing the token ( HMAC USING SHA-256)
ALGORITHM = "HS256"
# 30 mins time set for expiration
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# server will check whether the token is valid or not. lilke for example whoever bears ( or holds ) the token is granted access.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    # creating copy so as not to modify original dict.
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "sub": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # returns newly created token string
    return encoded_jwt

# model.user type hint indicating function is expected to run an instance of user model.
def get_current_user(
    db: Session = Depends(get_db),
    # this tells oauth2_scheme to get the token from the requests authorization header and pass it as the token argument.
    token: str = Depends(oauth2_scheme)
) -> models.User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user



def get_current_admin_user(current_user: models.User= Depends(get_current_user)) -> models.User:

    if current_user.role.value!='admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation forbidden: Admin privileges required",
        )
    
    return current_user