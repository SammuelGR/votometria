from fastapi import FastAPI

from app.routers.api import router as api_router


app = FastAPI(title="Votometria API")


@app.get("/health", tags=["Health"])
def read_health():
    return {"status": "ok"}


app.include_router(api_router)
