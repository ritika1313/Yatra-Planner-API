# This is my Entry point file
from pathlib import Path
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.routes.planner import router
from app.routes.stream import router as stream_router

app = FastAPI(
    title="Yatra Planner API",
    description="Aggregrate travel data from multiple sources to provide a single plan with SSE support",
    version="1.0.0",
)

@app.get("/")
async def root():
    return{
        "app": "Yatra Planner API",
        "version": "1.0.0",
        "endpoints": {
            "POST /plan": "Create a travel plan (Aggregated)",
            "GET /plan/stream": "Stream a travel plan (SSE)",
            "GET /plan/cache-stats": "View Cache Statistics for travel plans",
            "DELETE /plan/cache": "Clear for travel plans",
        }
    }

app.include_router(router)
app.include_router(stream_router)
