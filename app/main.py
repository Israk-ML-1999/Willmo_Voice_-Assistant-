from fastapi import FastAPI
from app.micro_goals.router import router as microgoals_router
from app.Voice_assistant.voice_router import router as voice_router 
from app.chat.chat_router import router as chat_router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# Mount routers
app.include_router(microgoals_router, prefix="/api/microgoals", tags=["Micro Goals"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice Assistant"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} is running!"}

