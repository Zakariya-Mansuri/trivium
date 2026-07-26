from fastapi import APIRouter

from app.api.routes import agent, auth, learn, metrics, profile, projects, reviews, sessions

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(sessions.router)
api_router.include_router(agent.router)
api_router.include_router(learn.router)
api_router.include_router(reviews.router)
api_router.include_router(profile.router)
api_router.include_router(metrics.router)
