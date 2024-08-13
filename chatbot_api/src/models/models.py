from pydantic import BaseModel


class ProcessInput(BaseModel):
    data: str

    class Config:
        arbitrary_types_allowed = True
