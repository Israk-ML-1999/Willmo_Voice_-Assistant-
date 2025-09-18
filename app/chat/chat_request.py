from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatTextRequest(BaseModel):
    user_id: Optional[str] = None
    user_query: str = Field(..., min_length=1)
    user_age: int = Field(..., ge=1, le=120)
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None, 
        description="List of previous conversation messages with user_query and ai_response keys"
    )

class ChatTextResponse(BaseModel):
    answer: str = ""