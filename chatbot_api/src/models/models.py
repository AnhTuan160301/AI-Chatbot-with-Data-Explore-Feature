from pydantic import BaseModel


class ProcessInput(BaseModel):
    data: str | None
    user_message: str


class QueryInput(BaseModel):
    user_message: str


class ProcessOutput(BaseModel):
    input: str
    output: str
