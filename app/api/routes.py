from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.services.langchain_service import LangChainService
from app.models.request_models import PingRequest, ChatRequest, AnalysisRequest
from app.utils.app_utils import make_analysis_data
from app.services.analysis_service import process_analysis_in_background
from typing import Dict
import httpx
import uuid
from datetime import datetime
from app.utils.task_manager import init_task_status, get_task_status

router = APIRouter()
langchain_service = LangChainService( model_type="openai" )

# 작업 상태를 저장할 딕셔너리
task_status: Dict[str, Dict] = {}

@router.post("/ping")
async def ping(request: PingRequest):
    return { "response": "ok" }

@router.post("/chat")
async def chat(request: ChatRequest):
    response = await langchain_service.process_chat(request.query)
    return {"response": response}

@router.post("/analysis")
async def analysis(data: dict, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    elk_id = data.get("elk_id", "")
    ai_model = data.get("ai_model", "")
    
    # 작업 상태 초기화
    init_task_status(task_id)
    
    # 백그라운드 작업 추가
    background_tasks.add_task(
        process_analysis_in_background,
        task_id=task_id,
        elk_id=elk_id,
        ai_model=ai_model,
        data=data,
        callback_api=""
    )
    
    return {"task_id": task_id}

@router.get("/analysis/{task_id}")
async def get_analysis_status(task_id: str):
    status = get_task_status(task_id)
    if status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Task not found")
    return status