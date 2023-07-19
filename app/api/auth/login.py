from fastapi import Depends, HTTPException, status
from api.core.config import SECRET_KEY
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from api.auth.admin_auth import oauth2_bearer
from api.db.session import get_db
from api.models.models import UserModel

SECRET_KEY = SECRET_KEY


async def get_current_user(token: str = Depends(oauth2_bearer),
                           db: Session = Depends(get_db)):
    try:
        pyload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Update token")

    gmail: str = pyload.get("username")
    user_id: int = pyload.get("id")


    res = db.query(UserModel).filter(UserModel.gmail == gmail).first()

    if gmail is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )

    return {"sub": gmail, "user_id": user_id}
