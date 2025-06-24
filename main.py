from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api.api_v1.api import router as api_router
from core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="APIшка VKurseDerma",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to VKurseDerma API detka"}

@app.get("/health")
async def check_health():
    return {"status": "ok", "details": "API работает нормально"}


instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


Path("media").mkdir(exist_ok=True)
Path("thumbnails").mkdir(exist_ok=True)

app.mount("/media", StaticFiles(directory="media"), name="media")
app.mount("/thumbnails", StaticFiles(directory="thumbnails"), name="thumbnails")