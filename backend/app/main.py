from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routers import public, admin

app = FastAPI(
    title="Photo Album API",
    description="API для фотоальбому: публічний перегляд + адмінка для завантаження фото",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public.router)
app.include_router(admin.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
