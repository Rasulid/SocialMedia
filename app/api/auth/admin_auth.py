from fastapi import Depends, HTTPException, status, APIRouter
from passlib.exc import UnknownHashError

from api.core.config import SECRET_KEY
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from api.db.DataBasse import engine, SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime
from jose import jwt, JWTError

from api.models.models import UserModel, Base

SECRET_KEY = SECRET_KEY
ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token/")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Authenticate Error"}},
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def password_hash(password):
    if password is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="password is None")
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    if plain_password is None or hashed_password is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="failed verify password")
    try:
        return bcrypt_context.verify(plain_password, hashed_password)
    except UnknownHashError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unknown hash error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def authenticate_admin(gmail: str, password: str, db):
    user = db.query(UserModel).filter(UserModel.gmail == gmail).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user is not valid")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="password is not valid")
    return user


def create_access_token(
        username: str, user_id: int, express_delta: Optional[timedelta] = None
):
    encode = {"username": username, "id": user_id}
    if express_delta:
        expire = datetime.utcnow() + express_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=20)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


def create_refresh_token(
        username: str,
        user_id: int,
        express_delta: Optional[timedelta] = None
):
    encode = {"username": username, "id": user_id}
    if express_delta:
        expire = datetime.utcnow() + express_delta
    else:
        expire = datetime.utcnow() + timedelta(days=10)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


@router.post("/token")
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    try:
        user = authenticate_admin(form_data.username, form_data.password, db=db)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user is not valid")
    except HTTPException as error:
        print("__", error)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token_expires = timedelta(minutes=20)

    token = create_access_token(user.gmail, user.id, express_delta=token_expires)
    refresh_token = create_refresh_token(user.gmail, user.id)

    return {"access_token": token, "refresh_token": refresh_token}


def validate_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Add additional checks for the refresh token, if necessary
    return user_id


@router.post("/refresh_token")
async def refresh_token(refresh_token: str):
    user_id = validate_refresh_token(refresh_token)

    new_access_token = create_access_token(user_id, express_delta=timedelta(minutes=20))

    return {"access_token": new_access_token}


# Exceptions
def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response