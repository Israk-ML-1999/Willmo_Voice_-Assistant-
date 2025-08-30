from fastapi import APIRouter, HTTPException
from app.chat.chat_request import ChatTextRequest, ChatTextResponse
from app.chat.llm_service import chat_llm_service

router = APIRouter()

@router.post("/chat-text", response_model=ChatTextResponse, summary="Text chat (uses AGE_BASED_SYSTEM_PROMPT)")
async def chat_text(payload: ChatTextRequest):
    try:
        answer = chat_llm_service.generate_response(
            text=payload.user_query,
            user_age=payload.user_age,
            history=payload.history.dict() if payload.history else None
        )
        return ChatTextResponse(answer=answer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chat response: {str(e)}")
