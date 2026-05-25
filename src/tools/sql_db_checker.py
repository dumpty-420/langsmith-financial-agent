from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_anthropic import ChatAnthropic
from src.prompts.sql_prompts import get_sql_check_prompt

class SqlCheckerInput(BaseModel):
    query: str = Field(description="A SQL query to check before execution")

class SqlDbCheckerTool(BaseTool):
    name: str = "sql_db_query_checker"
    description: str = "Use this tool to double check if your query is correct before executing it with sql_db_query."
    args_schema: Type[BaseModel] = SqlCheckerInput

    def _run(self, query: str) -> str:
        llm = ChatAnthropic(model="claude-sonnet-4-6", max_retries=10)
        system_message = {
            "role": "system",
            "content": get_sql_check_prompt(),
        }
        user_message = {
            "role": "user",
            "content": f"Here is the SQL query:\n```sql\n{query}\n```",
        }
        response = llm.invoke([system_message, user_message])
        return response.content
