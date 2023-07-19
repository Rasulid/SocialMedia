import json
from datetime import datetime
from typing import List

from pydantic import BaseModel

from .image_schema import CreateImageSchema
from .user_schema import ReadUserSchema


class PostSchema(BaseModel):
    title: str
    content: str
    created_at: datetime


class ReadPostSchemaWithLikes(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    author: List[ReadUserSchema]
    image: List[CreateImageSchema]
    likes: int
    dislikes: int

    class Config:
        orm_mode = True


class ReadPostSchema(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    author: List[ReadUserSchema]
    image: List[CreateImageSchema]


    class Config:
        orm_mode = True


class CreatePostSchemas(PostSchema):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


