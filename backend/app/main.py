from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, simulations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: pre-warm Gemini model (fails gracefully if API key not set)
    try:
        from app.agents.gemini_client import get_model
        get_model()
    except Exception:
        pass
    yield
    # Shutdown: nothing to clean up (engine pools close automatically)


app = FastAPI(
    title="Albertsons Monte Carlo Simulation Platform",
    description="Production-grade e-commerce strategy simulator with Gemini AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://next-app:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(simulations.router)
