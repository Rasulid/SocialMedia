from pydantic import BaseModel


class CreateImageSchema(BaseModel):
    filename: str
    file_path: str

    class Config:
        orm_mode = True
