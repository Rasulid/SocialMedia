from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from api.db.session import get_db
from api.models.models import UserModel, PostModel, ImageModel
from api.schemas.user_schema import ReadUserSchema, CreateUserSchema, ReadUserSchemaWithPosts, ReadPostSchemaInPost
from api.auth.admin_auth import password_hash, login_for_access_token
from api.schemas.image_schema import CreateImageSchema
from api.auth.login import get_current_user
from api.core.config import SECRET_KEY
from api.auth.email_check import check_email

router = APIRouter(tags=["user"],
                   prefix="/api/users")


@router.post("/login", tags=['login'])
async def login(log: dict = Depends(login_for_access_token)):
    return log


@router.get("/user-me")
async def me(token: str,
             db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("id")
        query = db.query(UserModel).filter(UserModel.id == user_id).first()

        if query is None:
            query = db.query(UserModel).filter(UserModel.id == user_id).first()

        return query
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/list", response_model=List[ReadUserSchema])
async def list_users(db: Session = Depends(get_db),
                     login: dict = Depends(get_current_user)):
    query = db.query(UserModel).all()
    return query


@router.get("/{id}", response_model=ReadUserSchema)
async def get_user_by_id(id: int,
                         db: Session = Depends(get_db),
                         login: dict = Depends(get_current_user)):
    query = db.query(UserModel).filter(UserModel.id == id).first()

    if query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found"
        )

    return query


@router.post("/create", response_model=ReadUserSchema)
async def create_user(schema: CreateUserSchema,
                      db: Session = Depends(get_db)):
    query_to_email = db.query(UserModel) \
        .filter(UserModel.gmail == schema.gmail) \
        .first()

    query_to_username = db.query(UserModel) \
        .filter(UserModel.username == schema.username) \
        .first()

    user_model = UserModel()
    user_model.username = schema.username
    user_model.gmail = schema.gmail
    check =  check_email(user_model.gmail)

    if check == True:

        user_model.password = schema.password
        hashed_password = password_hash(schema.password)

        if query_to_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{user_model.gmail} is already in use"
            )

        if query_to_username is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{user_model.username} is already in use"
            )

        user_model.password = hashed_password

        db.add(user_model)
        db.commit()

        response = ReadUserSchema(
            id=user_model.id,
            username=user_model.username,
            gmail=user_model.gmail
        )

        return response

    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email {user_model.gmail} is not found"
        )


@router.put("/update/{id}", response_model=ReadUserSchema)
async def update_user(id: int,
                      schema: CreateUserSchema,
                      db: Session = Depends(get_db),
                      login: dict = Depends(get_current_user)):

    query = db.query(UserModel) \
        .filter(UserModel.id == id) \
        .first()

    if query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found"
        )

    query.username = schema.username
    query.gmail = schema.gmail

    check = check_email(query.gmail)

    if check == True:

        query.password = schema.password

        db.add(query)
        db.commit()

        return query

    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email {query.gmail} is not found"
        )




@router.delete("/delete-post/{id}")
async def delete(id: int,
                 db: Session = Depends(get_db),
                 login: dict = Depends(get_current_user)):
    query_to_exicis = db.query(UserModel) \
        .filter(UserModel.id == id) \
        .first()

    if query_to_exicis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found"
        )

    query_to_delete = db.query(UserModel) \
        .filter(UserModel.id == id) \
        .delete()

    db.commit()

    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content="User deleted",
    )


@router.get("/user-with-posts/{id}", response_model=ReadUserSchemaWithPosts)
async def user_with_posts(id: int, db: Session = Depends(get_db),
                          login: dict = Depends(get_current_user)):
    user = db.query(UserModel).filter(UserModel.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    posts = db.query(PostModel).filter(PostModel.author_id == user.id).all()

    posts_with_images = []
    for post in posts:
        images = db.query(ImageModel).filter(ImageModel.post_id == post.id).all()
        read_post = ReadPostSchemaInPost(
            id=post.id,
            title=post.title,
            content=post.content,
            created_at=post.created_at,
            image=[CreateImageSchema(filename=image.filename, file_path=image.file_path) for image in images]
        )
        posts_with_images.append(read_post)

    user_with_posts = ReadUserSchemaWithPosts(
        id=user.id,
        username=user.username,
        gmail=user.gmail,
        posts=posts_with_images
    )

    return user_with_posts
