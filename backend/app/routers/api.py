from fastapi import APIRouter

from app.routers.current_election import router as current_election_router


router = APIRouter(prefix="/api")

router.include_router(
    current_election_router,
    prefix="/current-election",
    tags=["Current Election"],
)
