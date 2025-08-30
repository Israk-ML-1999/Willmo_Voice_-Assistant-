from pydantic import BaseModel, Field
from typing import Optional

class ChatHistory(BaseModel):
    message: str = ""
    response: str = ""

class ChatTextRequest(BaseModel):
    user_id: Optional[str] = None
    user_query: str = Field(..., min_length=1)
    user_age: int = Field(..., ge=1, le=120)
    history: Optional[ChatHistory] = None

class ChatTextResponse(BaseModel):
    answer: str= ""
