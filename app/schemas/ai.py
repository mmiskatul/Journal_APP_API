from pydantic import BaseModel


class AIMessage(BaseModel):
    role: str
    content: str


class AIRequest(BaseModel):
    messages: list[AIMessage]


class AIResponse(BaseModel):
    reply: str
