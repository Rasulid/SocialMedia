from datetime import datetime
from typing import List

from pydantic import BaseModel

from api.schemas.image_schema import CreateImageSchema


class ReadPostSchemaInPost(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    image: List[CreateImageSchema]


class CreateUserSchema(BaseModel):
    username: str
    gmail: str
    password: str


class ReadUserSchema(BaseModel):
    id: int
    username: str
    gmail: str

    class Config:
        orm_mode = True


class ReadUserSchemaWithPosts(BaseModel):
    id: int
    username: str
    gmail: str
    posts: List[ReadPostSchemaInPost]

    class Config:
        orm_mode = True


