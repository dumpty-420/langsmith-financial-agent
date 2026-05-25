from typing import Type, Any
import os
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

class SchemaInput(BaseModel):
    query: str = Field(description="Any string query to get the schema.")

class SqlDbSchemaTool(BaseTool):
    name: str = "sql_db_schema"
    description: str = "Gets the database schema of Transaction_DB."
    args_schema: Type[BaseModel] = SchemaInput

    def _run(self, query: str) -> str:
        current_dir = Path(__file__).parent
        schema_path = current_dir.parent / "configs" / "schema.json"
        try:
            with open(schema_path, "r") as f:
                schema = f.read()
            return schema
        except FileNotFoundError:
            return "Schema file not found."
