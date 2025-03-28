from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.services.langchain_service import LangChainService
from app.models.request_models import PingRequest, ChatRequest, AnalysisRequest
from app.utils.app_utils import make_analysis_data
from typing import Dict
import httpx

router = APIRouter()
langchain_service = LangChainService()

@router.post("/ping")
async def ping(request: PingRequest):
    return { "response": "ok" }

@router.post("/chat")
async def chat(request: ChatRequest):
    response = await langchain_service.process_chat(request.query)
    return {"response": response}

async def process_analysis_in_background(battle_data: dict, callback_api: str):
    try:
        user_data = make_analysis_data(battle_data, "result_info", "user_record_minimal")
        verify_data = make_analysis_data(battle_data, "result_info", "verify_record_minimal")
        
        result = await langchain_service.run(user_data, verify_data, ["status", "hp"])
        
        async with httpx.AsyncClient() as client:
            await client.post(callback_api, json={
                "status": "completed",
                "result": result
            })
    except Exception as e:
        async with httpx.AsyncClient() as client:
            await client.post(callback_api, json={
                "status": "failed",
                "error": str(e)
            })

@router.post("/analysis")
async def analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):

    callback_api = "testtest"
    # 백그라운드 작업 시작
    background_tasks.add_task(process_analysis_in_background, request.battle_data, callback_api)
    
    return {
        "status": "processing",
        "message": "Analysis started in background"
    }