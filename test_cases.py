import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app  # Import your FastAPI app

# Initialize the FastAPI test client
client = TestClient(app)

# Mock Redis client
mock_redis = MagicMock()

# Mock Celery task
mock_task = MagicMock()
mock_task.id = "mock-task-id"

# Mock Redis response
mock_redis.get.return_value = '{"results": {"files": [], "summary": {"total_files": 0, "total_issues": 0}}}'


@pytest.fixture
def mock_dependencies():
    """
    Fixture to mock Redis and Celery dependencies for tests.
    """
    with patch("tasks.redis_client", mock_redis), patch("tasks.analyze_pr_task.delay", return_value=mock_task):
        yield


def test_analyze_endpoint(mock_dependencies):
    """
    Test the /analyze endpoint for successful task submission.
    """
    payload = {"repository_url": "https://github.com/example/repo", "pull_request_number": 123}
    response = client.post("/analyze", json=payload)

    assert response.status_code == 200
    assert "task_id" in response.json()
    assert response.json()["task_id"] == "mock-task-id"


def test_status_endpoint_pending(mock_dependencies):
    """
    Test the /status endpoint for a PENDING task.
    """
    # Simulate a PENDING task state
    with patch("main.AsyncResult") as mock_async_result:
        mock_async_result.return_value.status = "PENDING"
        response = client.get(f"/status/{mock_task.id}")

    assert response.status_code == 200
    assert response.json()["task_id"] == "mock-task-id"
    assert response.json()["status"] == "PENDING"


def test_status_endpoint_success(mock_dependencies):
    """
    Test the /status endpoint for a SUCCESS task.
    """
    # Simulate a SUCCESS task state
    with patch("main.AsyncResult") as mock_async_result:
        mock_async_result.return_value.status = "SUCCESS"
        response = client.get(f"/status/{mock_task.id}")

    assert response.status_code == 200
    assert response.json()["task_id"] == "mock-task-id"
    assert response.json()["status"] == "SUCCESS"


def test_result_endpoint(mock_dependencies):
    """
    Test the /result endpoint for a task with results.
    """
    # Simulate a valid Redis response for the task ID
    mock_redis.get.return_value = '{"results": {"files": [], "summary": {"total_files": 0, "total_issues": 0}}}'

    response = client.get(f"/result/{mock_task.id}")

    assert response.status_code == 200
    assert "results" in response.json()
    assert response.json()["results"]["summary"]["total_files"] == 0
    assert response.json()["results"]["summary"]["total_issues"] == 0



def test_result_endpoint_missing(mock_dependencies):
    """
    Test the /result endpoint for a missing task result in Redis.
    """
    mock_redis.get.return_value = None  # Simulate missing Redis key
    response = client.get(f"/result/{mock_task.id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Result not found. The task may still be processing or the data has expired."
