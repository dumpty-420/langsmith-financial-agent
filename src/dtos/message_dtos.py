from pydantic import BaseModel
from typing import Optional

class AnalysisRequest(BaseModel):
    id: int

class AnalysisResponse(BaseModel):
    id: int
    analysis: str
    status: str
