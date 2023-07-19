from pydantic import BaseModel


class LikeSchema(BaseModel):
    user_id: int
    post_id: int
    is_liked: bool

    class Config:
        orm_mode = True


class DislikeSchema(BaseModel):
    user_id: int
    post_id: int
    is_liked: bool

    class Config:
        orm_mode = True
