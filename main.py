import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env variables for LangSmith
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "financial-analysis-agent")

from src.routes.analysis_route import analysis_router
from src.routes.health_route import health_route
from src.configs.logger_config import get_logger

logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Financial Analysis Service")
    yield
    logger.info("Shutting down Financial Analysis Service")

app = FastAPI(
    title="Financial Analysis Service",
    description="AI agents for SQL-based financial analysis on Transaction_DB",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)
app.include_router(health_route)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
