import os
from typing import Optional
from threading import Lock
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import URL

class PostgresConnectionPool:
    """
    Singleton class for managing PostgreSQL connection pool using SQLAlchemy.
    """
    _instance: Optional['PostgresConnectionPool'] = None
    _lock: Lock = Lock()
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None

    def __new__(cls) -> 'PostgresConnectionPool':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self) -> None:
        if self._engine is None:
            with self._lock:
                if self._engine is None:
                    self._initialize_pool()

    def _initialize_pool(self) -> None:
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "admin"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "Transaction_DB")
        )

        self._engine = create_engine(
            url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600
        )

        self._session_factory = sessionmaker(
            bind=self._engine,
            expire_on_commit=False
        )

    def get_session(self) -> Session:
        if self._session_factory is None:
            raise RuntimeError("Database session factory not initialized")
        return self._session_factory()

    def execute_query(self, query: str, params: Optional[dict] = None) -> list[dict]:
        with self.get_session() as session:
            try:
                result = session.execute(text(query), params or {})
                return [dict(row) for row in result.mappings()]
            except SQLAlchemyError as e:
                session.rollback()
                raise e

db_obj = PostgresConnectionPool()
