import glob
import os
import shutil
import uuid
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy import false
from sqlalchemy.orm import Session, joinedload
from starlette.responses import JSONResponse

from api.db.session import get_db
from api.models.models import PostModel, ImageModel, LikeModel
from api.schemas.image_schema import CreateImageSchema
from api.schemas.post_schema import CreatePostSchemas, ReadPostSchema, ReadPostSchemaWithLikes
from api.auth.login import get_current_user

router = APIRouter(tags=["Post"],
                   prefix="/api/post")


@router.get("/list", response_model=List[ReadPostSchemaWithLikes])
async def list_post(db: Session = Depends(get_db)):
    query = db.query(PostModel) \
        .join(ImageModel, PostModel.id == ImageModel.post_id) \
        .options(joinedload(PostModel.image)) \
        .all()
    response = []
    for x in query:
        likes = db.query(LikeModel).filter(LikeModel.post_id == x.id, LikeModel.is_liked == True).count()
        dislikes = db.query(LikeModel).filter(LikeModel.post_id == x.id, LikeModel.is_liked == False).count()
        res = ReadPostSchemaWithLikes(
            id=x.id,
            title=x.title,
            content=x.content,
            created_at=x.created_at,
            author=[x.author],
            image=x.image,
            likes=likes,
            dislikes=dislikes
        )
        response.append(res)

    return response


@router.get("/get/{id}", response_model=ReadPostSchemaWithLikes)
async def get_post(id: int, db: Session = Depends(get_db)):
    query = db.query(PostModel).filter(PostModel.id == id) \
        .join(ImageModel, PostModel.id == ImageModel.post_id) \
        .options(joinedload(PostModel.image)) \
        .first()

    if query is None:
        raise HTTPException(status_code=404, detail="Post not found")

    likes = db.query(LikeModel).filter(LikeModel.post_id == query.id, LikeModel.is_liked == True).count()
    dislikes = db.query(LikeModel).filter(LikeModel.post_id == query.id, LikeModel.is_liked == False).count()

    response = ReadPostSchemaWithLikes(
        id=query.id,
        title=query.title,
        content=query.content,
        created_at=query.created_at,
        author=[query.author],
        image=query.image,
        likes=likes,
        dislikes=dislikes
    )

    return response




async def upload_img(file: List[UploadFile] = File(...)):
    image_list = []
    for img in file:
        img.filename = f"{uuid.uuid4()}.jpg"
        with open(f"media/{img.filename}", "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)
            append_for_db = CreateImageSchema(filename=img.filename, file_path=f"media/")
        image_list.append(append_for_db)
    return image_list


@router.post("/create")
async def create_post(schema: CreatePostSchemas,
                      db: Session = Depends(get_db),
                      file: List[UploadFile] = File(),
                      login: dict = Depends(get_current_user)):
    id = login.get('user_id')
    res = []
    upload_image = await upload_img(file)

    result = []

    post_model = PostModel()
    post_model.title = schema.title
    post_model.content = schema.content
    post_model.created_at = schema.created_at
    post_model.author_id = id

    db.add(post_model)
    db.commit()

    res.append(post_model)

    for x in upload_image:
        image_model = ImageModel()
        image_model.post_id = post_model.id
        image_model.file_path = x.file_path
        image_model.filename = x.filename
        result.append(image_model)

    db.add_all(result)
    db.commit()

    res.append(result)

    response = ReadPostSchema(
        id=post_model.id,
        title=post_model.title,
        content=post_model.content,
        created_at=post_model.created_at,
        author=[post_model.author],
        image=result
    )

    return response


@router.put("/update/{id}")
async def update_product(
        id: int,
        schema: CreatePostSchemas,
        db: Session = Depends(get_db),
        file: List[UploadFile] = File(),
        login: dict = Depends(get_current_user)
):
    owner_id = login.get("user_id")
    res = []
    upload_image = await upload_img(file)

    result = []

    post_model = db.query(PostModel).filter(PostModel.id == id).first()

    if post_model is not None:
        post_model.title = schema.title
        post_model.content = schema.content
        post_model.created_at = schema.created_at
        post_model.author_id = owner_id

        res.append(post_model)

        image_models = db.query(ImageModel).filter(ImageModel.post_id == id).all()
        for image in image_models:
            os.remove(image.file_path + '/' + image.filename)
            if os.path.exists(image.file_path + '/' + image.filename) is false:
                return True

        db.query(ImageModel).filter(ImageModel.post_id == id).delete()

        new_image_models = []
        for x in upload_image:
            new_image = ImageModel(
                file_path=x.file_path,
                filename=x.filename,

            )
            new_image_models.append(new_image)

        db.add_all(new_image_models)
        db.commit()

        post_model.image = new_image_models

        db.add_all(result)
        db.commit()
        db.add(post_model)
        db.commit()


        response = ReadPostSchema(
            id=post_model.id,
            title=post_model.title,
            content=post_model.content,
            created_at=post_model.created_at,
            author=[post_model.author],
            image=post_model.image,
        )

        return response

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content="Product not found"
    )

@router.delete("/delete/{id}")
async def delete_post(
        id: int,
        db: Session = Depends(get_db),
        login: dict = Depends(get_current_user)
):
    owner_id = login.get("user_id")

    post_model = db.query(PostModel).filter(PostModel.id == id).options(joinedload(PostModel.author)).first()

    if post_model is not None and post_model.author_id == owner_id:
        image_models = db.query(ImageModel).filter(ImageModel.post_id == id).all()
        for image in image_models:
            file_name = os.path.join(image.file_path, image.filename)
            if os.path.exists(file_name):
                os.remove(file_name)

        db.delete(post_model)
        db.query(ImageModel).filter(ImageModel.post_id == id).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content="post was deleted"
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found or you don't have permission to delete.")