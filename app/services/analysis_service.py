import httpx
from app.services.langchain_service import LangChainService
from app.utils.app_utils import make_analysis_data
from app.utils.task_manager import update_task_status
from app.config.app_config import app_config
from datetime import datetime

def get_callback_url() -> str:
    """Battle Verifier 서버의 콜백 URL을 생성합니다."""
    verifier_config = app_config["battle_verifier"]
    return f"{verifier_config['protocol']}://{verifier_config['host']}:{verifier_config['port']}/api/report_gen_finish"

async def process_analysis_in_background(task_id: str, elk_id: str, provider: str, model: str, temperature: float, battle_data: dict, callback_api: str):
    try:
        user_data = make_analysis_data(battle_data, "result_info", "user_record_minimal")
        verify_data = make_analysis_data(battle_data, "result_info", "verify_record_minimal")
        
        # 분석 서비스 초기화
        langchain_service = LangChainService(provider=provider, model=model, temperature=temperature)
        
        # 분석 실행
        result = await langchain_service.run(
            user_data=user_data,
            verify_data=verify_data,
            report_types=["status", "hp", "attack"]
        )
        
        # 콜백 API 호출
        callback_url = get_callback_url()
        async with httpx.AsyncClient() as client:
            await client.post(callback_url, json={
                "task_id": task_id,
                "elk_id": elk_id,
                "provider": provider,
                "ai_model": model,
                "temperature": temperature,
                "status": "completed",
                "result": result
            })
        
        # 작업 상태 업데이트
        update_task_status(task_id, "completed", result=result)
        
    except Exception as e:
        # 에러 발생 시 콜백 API 호출
        callback_url = get_callback_url()
        async with httpx.AsyncClient() as client:
            await client.post(callback_url, json={
                "task_id": task_id,
                "elk_id": elk_id,
                "provider": provider,
                "ai_model": model,
                "temperature": temperature,
                "status": "failed",
                "error": str(e)
            })
        
        # 작업 상태 업데이트
        update_task_status(task_id, "failed", error=str(e)) 