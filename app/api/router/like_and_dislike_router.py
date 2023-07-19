from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.db.session import get_db
from api.models.models import LikeModel, PostModel
from api.schemas.like_dislike_schema import LikeSchema, DislikeSchema

router = APIRouter(tags=["like and dislike"],
                   prefix="/api/like-and-dislike")


@router.post("/like/", response_model=LikeSchema)
def create_like(like_data: LikeSchema, db: Session = Depends(get_db)):
    existing_like = db.query(LikeModel).filter(LikeModel.user_id == like_data.user_id,
                                               LikeModel.post_id == like_data.post_id).first()

    post = db.query(PostModel).filter(PostModel.id == like_data.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id == like_data.user_id:
        raise HTTPException(status_code=400, detail="Cannot like your own post")

    if existing_like:
        raise HTTPException(status_code=400, detail="Like already exists")

    like = LikeModel(**like_data.dict())
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


@router.delete("/like/{like_id}/", response_model=LikeSchema)
def delete_like(like_id: int, db: Session = Depends(get_db)):
    like = db.query(LikeModel).filter(LikeModel.id == like_id).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                        content="Like deleted")


@router.post("/dislike/", response_model=LikeSchema)
def create_dislike(dislike_data: LikeSchema, db: Session = Depends(get_db)):
    existing_like = db.query(LikeModel).filter(LikeModel.user_id == dislike_data.user_id,
                                               LikeModel.post_id == dislike_data.post_id).first()

    existing_dislike = db.query(LikeModel).filter(LikeModel.user_id == dislike_data.user_id,
                                                  LikeModel.post_id == dislike_data.post_id,
                                                  LikeModel.is_liked == False).first()

    post = db.query(PostModel).filter(PostModel.id == dislike_data.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id == dislike_data.user_id:
        raise HTTPException(status_code=400, detail="Cannot dislike your own post")

    if existing_like:
        raise HTTPException(status_code=400, detail="Cannot dislike a post you liked")

    if existing_dislike:
        raise HTTPException(status_code=400, detail="Dislike already exists")

    dislike_data.is_liked = False
    dislike = LikeModel(**dislike_data.dict())
    db.add(dislike)
    db.commit()
    db.refresh(dislike)
    return dislike



@router.delete("/dislike/{dislike_id}/", response_model=DislikeSchema)
def delete_dislike(dislike_id: int, db: Session = Depends(get_db)):
    dislike = db.query(LikeModel).filter(LikeModel.id == dislike_id).first()
    if not dislike:
        raise HTTPException(status_code=404, detail="Dislike not found")

    db.delete(dislike)
    db.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                        content="Dislike deleted")