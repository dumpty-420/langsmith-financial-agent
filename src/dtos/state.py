from pydantic import BaseModel
from typing import Any, Optional

class State(BaseModel):
    messages: Any = None
    table_metadata: Optional[str] = None
    sql_query: Optional[str] = None
    search_results: Optional[list] = None
    structured_analysis: Optional[str] = None
