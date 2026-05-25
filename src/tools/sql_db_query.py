import re
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from src.database.postgres_db import PostgresConnectionPool

class SqlInput(BaseModel):
    query: str = Field(description="A SQL query to execute against the database")

class SqlDbQueryTool(BaseTool):
    name: str = "sql_db_query"
    description: str = "Execute a SQL query against the database and return the result. Input must be a SQL query."
    args_schema: Type[BaseModel] = SqlInput

    @staticmethod
    def clean_sql_query(sql_query: str) -> str:
        if not sql_query:
            return sql_query
        cleaned = re.sub(r'^```sql\s*\n?', '', sql_query, flags=re.MULTILINE | re.IGNORECASE)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip('`').strip()
        return cleaned

    def _run(self, query: str) -> str:
        session_obj = PostgresConnectionPool()
        try:
            cleaned_sql = self.clean_sql_query(query)
            response = session_obj.execute_query(cleaned_sql)
            return str(response)
        except Exception as e:
            return f"Error executing query: {str(e)}"
