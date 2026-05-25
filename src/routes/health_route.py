from fastapi import APIRouter
from src.database.postgres_db import PostgresConnectionPool

health_route = APIRouter(
    prefix="/api/health",
    tags=["Health"]
)

@health_route.get("/")
def health_check():
    try:
        db = PostgresConnectionPool()
        # Test connection
        db.execute_query("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
