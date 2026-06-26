from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_cors_origins
from app.core.error_handlers import register_error_handlers
from app.routers.api import router as api_router


app = FastAPI(title="Votometria API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(get_cors_origins()),
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)


@app.get("/health", tags=["Health"])
def read_health():
    return {"status": "ok"}


app.include_router(api_router)
