from typing import Dict, Any
from datetime import datetime

# 작업 상태를 저장하는 전역 딕셔너리
task_status: Dict[str, Dict[str, Any]] = {}

def init_task_status(task_id: str) -> None:
    """새로운 작업의 상태를 초기화합니다."""
    task_status[task_id] = {
        "status": "pending",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "result": None,
        "error": None
    }

def update_task_status(task_id: str, status: str, result: Any = None, error: str = None) -> None:
    """작업 상태를 업데이트합니다."""
    if task_id in task_status:
        task_status[task_id]["status"] = status
        if status == "completed":
            task_status[task_id]["completed_at"] = datetime.utcnow().isoformat()
            task_status[task_id]["result"] = result
        elif status == "failed":
            task_status[task_id]["error"] = error

def get_task_status(task_id: str) -> Dict[str, Any]:
    """작업 상태를 조회합니다."""
    return task_status.get(task_id, {"status": "not_found"}) 