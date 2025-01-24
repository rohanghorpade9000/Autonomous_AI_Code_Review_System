from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from celery import Celery
from celery.result import AsyncResult
from tasks import analyze_pr_task
from redis_client import redis_client
import json

# Initialize FastAPI application
# This serves as the entry point for defining API endpoints
app = FastAPI()

# Initialize Celery application
# Celery is used here to handle background task processing with Redis as the broker and backend
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Define the request model for input validation using Pydantic
# This ensures that incoming requests have the expected structure
class AnalyzeRequest(BaseModel):
    repository_url: str  # URL of the GitHub repository
    pull_request_number: int  # Number of the pull request to analyze


# FastAPI endpoint to submit an analysis task
@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Submits a pull request analysis task to Celery.

    Args:
        request (AnalyzeRequest): Contains repository URL and pull request number.

    Returns:
        dict: A message indicating success and the ID of the submitted task.
    """
    try:
        # Submit the task to Celery for background processing
        task = analyze_pr_task.delay(request.repository_url, request.pull_request_number)

        # Respond with the task ID
        return {
            "message": "Analysis task submitted successfully.",
            "task_id": task.id
        }
    except Exception as e:
        # Handle and return internal server errors
        raise HTTPException(status_code=500, detail=str(e))

# FastAPI endpoint to check the status of a submitted task
@app.get("/status/{task_id}")
def get_status(task_id: str):
    """
    Retrieves the current status of a submitted Celery task.

    Args:
        task_id (str): The ID of the Celery task.

    Returns:
        dict: The current status of the task, including error details if it failed.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    status = task_result.status
    response = {"task_id": task_id, "status": status}

    # Include error details if the task has failed
    if status == "FAILURE":
        response["error"] = str(task_result.result)

    return response

# FastAPI endpoint to fetch the result of a completed task
@app.get("/result/{task_id}")
def get_result(task_id: str):
    """
    Retrieves the result of a completed Celery task from Redis.

    Args:
        task_id (str): The ID of the Celery task.

    Returns:
        dict: The result of the task, including status and additional data if available.

    Raises:
        HTTPException: If the result is not found or cannot be processed.
    """
    try:
        # Retrieve the task result from Redis
        raw_result = redis_client.get(f"task:result:{task_id}")

        if not raw_result:
            # Handle missing results in Redis
            raise HTTPException(status_code=404, detail="Result not found. The task may still be processing or the data has expired.")

        # Parse the raw result from JSON
        try:
            parsed_result = json.loads(raw_result)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to parse the result from Redis.")

        # Respond with the task result
        return {
            "task_id": task_id,
            "status": "SUCCESS",  # Assume success if data is retrieved
            **parsed_result  # Merge parsed result into the response
        }

    except HTTPException as e:
        # Re-raise known HTTP exceptions for consistency
        raise e
    except Exception as e:
        # Handle and log unexpected errors
        raise HTTPException(status_code=500, detail=str(e))
