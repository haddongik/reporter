from fastapi import APIRouter
from app.services.langchain_service import LangChainService
from app.models.request_models import ChatRequest, AnalysisRequest

router = APIRouter()
langchain_service = LangChainService()

@router.post("/chat")
async def chat(request: ChatRequest):
    response = await langchain_service.process_chat(request.query)
    return {"response": response}

@router.post("/analysis")
async def analysis(request: AnalysisRequest):
    analysis = await langchain_service.process_analyze(
        original_text=request.original_text,
        comparison_text=request.comparison_text
    )
    return {"analysis": analysis} 