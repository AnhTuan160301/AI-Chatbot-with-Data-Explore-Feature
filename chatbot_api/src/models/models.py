from typing import List

from pydantic import BaseModel


class ProcessInput(BaseModel):
    data: str | List[List[str]]

    class Config:
        arbitrary_types_allowed = True
