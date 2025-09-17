from openai import OpenAI
from fastapi import HTTPException
from typing import Optional, Dict
from app.config import settings


class ChatLLMService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE
        )

    def generate_response(
        self,
        text: str,
        user_age: int,
        history: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate a chat response using AGE_BASED_SYSTEM_PROMPT.

        Input:
            - text: user query
            - user_age: int
            - history: optional { "message": "...", "response": "..." }

        Output:
            - str (chat answer)
        """

        try:
            messages = [{"role": "system", "content": settings.AGE_BASED_SYSTEM_PROMPT}]

            # Add history if given
            if history:
                if history.get("message"):
                    messages.append({"role": "user", "content": history["message"]})
                if history.get("response"):
                    messages.append({"role": "assistant", "content": history["response"]})

            # Add user message with age context
            user_message = f"User Age: {user_age}\nQuery: {text}"
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=messages,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating chat response: {str(e)}")


# Singleton
chat_llm_service = ChatLLMService()
