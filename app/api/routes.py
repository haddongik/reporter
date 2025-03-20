from fastapi import APIRouter
from app.services.langchain_service import LangChainService
from app.models.request_models import ChatRequest

router = APIRouter()
langchain_service = LangChainService()

@router.post("/chat")
async def chat(request: ChatRequest):
    response = await langchain_service.process_query(request.query)
    return {"response": response} 