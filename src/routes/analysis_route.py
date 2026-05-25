from fastapi import APIRouter, HTTPException
from src.dtos.message_dtos import AnalysisRequest, AnalysisResponse
from src.agents.financial_agent import FinancialAgent
from langsmith import traceable

analysis_router = APIRouter(
    prefix="/api/analysis",
    tags=["Analysis"]
)

@analysis_router.post("/cashflow", response_model=AnalysisResponse)
@traceable(name="cashflow_analysis_post", tags=["route:cashflow"])
async def analyze_cashflow(request: AnalysisRequest):
    try:
        agent = FinancialAgent()
        result_text = await agent.analyze(request.id)
        return AnalysisResponse(
            id=request.id,
            analysis=result_text,
            status="completed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@analysis_router.get("/cashflow/{id}", response_model=AnalysisResponse)
@traceable(name="cashflow_analysis_get", tags=["route:cashflow"])
async def analyze_cashflow_get(id: int):
    try:
        agent = FinancialAgent()
        result_text = await agent.analyze(id)
        return AnalysisResponse(
            id=id,
            analysis=result_text,
            status="completed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
