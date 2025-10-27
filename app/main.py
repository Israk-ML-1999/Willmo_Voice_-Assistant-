from fastapi import FastAPI
from app.micro_goals.router import router as microgoals_router
from app.Voice_assistant.voice_router import router as voice_router 
from app.chat.chat_router import router as chat_router
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles
from app.cleanup_audio import start_cleanup_thread

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# Fixed middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/audio", StaticFiles(directory="/app/audio"), name="audio")
# Mount routers
app.include_router(microgoals_router, prefix="/api/microgoals", tags=["Micro Goals"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice Assistant"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])

@app.on_event("startup")
def on_startup():
    start_cleanup_thread()
    print("[Startup] Cleanup thread running inside Docker container")

@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} is running!"}

