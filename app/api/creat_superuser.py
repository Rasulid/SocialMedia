from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from api.auth.admin_auth import password_hash
from api.db.session import get_db
from api.models.models import UserModel

router = FastAPI(title="SuperUser")


@router.post("/create/root/superuser")
async def register(db: Session = Depends(get_db)):
    admin_model = UserModel()
    admin_model.name = "rasul"
    admin_model.age = 20
    admin_model.phone_number = "914774712"
    admin_model.gmail = "root@root.com"
    admin_model.password = "root"


    hash_password = password_hash('root')  # Make sure to implement this function correctly
    admin_model.password = hash_password

    user_name = db.query(UserModel).all()
    for x in user_name:
        if admin_model.gmail == x.gmail:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="user is already exists"
            )

    db.add(admin_model)
    db.commit()

    return "Success"
