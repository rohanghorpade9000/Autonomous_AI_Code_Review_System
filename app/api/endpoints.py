from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from celery.result import AsyncResult
from app.tasks.tasks import analyze_pr_task
from app.utils.redis_client import redis_client
import json

router = APIRouter()

class AnalyzeRequest(BaseModel):
    repository_url: str
    pull_request_number: int

@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        task = analyze_pr_task.delay(request.repository_url, request.pull_request_number)
        return {"message": "Analysis task submitted successfully.", "task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}")
def get_status(task_id: str):
    task_result = AsyncResult(task_id)
    status = task_result.status
    response = {"task_id": task_id, "status": status}
    if status == "FAILURE":
        response["error"] = str(task_result.result)
    return response

@router.get("/result/{task_id}")
def get_result(task_id: str):
    try:
        raw_result = redis_client.get(f"task:result:{task_id}")
        if not raw_result:
            raise HTTPException(status_code=404, detail="Result not found.")
        parsed_result = json.loads(raw_result)
        return {"task_id": task_id, "status": "SUCCESS", **parsed_result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
