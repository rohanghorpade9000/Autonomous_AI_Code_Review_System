import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)
mock_redis = MagicMock()
mock_task = MagicMock()
mock_task.id = "mock-task-id"
mock_redis.get.return_value = '{"results": {"files": [], "summary": {"total_files": 0, "total_issues": 0}}}'

@pytest.fixture
def mock_dependencies():
    with patch("app.tasks.tasks.redis_client", mock_redis), patch("app.tasks.tasks.analyze_pr_task.delay", return_value=mock_task):
        yield

def test_analyze_endpoint(mock_dependencies):
    payload = {"repository_url": "https://github.com/example/repo", "pull_request_number": 123}
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    assert "task_id" in response.json()
    assert response.json()["task_id"] == "mock-task-id"

def test_status_endpoint_pending(mock_dependencies):
    with patch("app.api.endpoints.AsyncResult") as mock_async_result:
        mock_async_result.return_value.status = "PENDING"
        response = client.get(f"/status/{mock_task.id}")
    assert response.status_code == 200
    assert response.json()["task_id"] == "mock-task-id"
    assert response.json()["status"] == "PENDING"

def test_status_endpoint_success(mock_dependencies):
    with patch("app.api.endpoints.AsyncResult") as mock_async_result:
        mock_async_result.return_value.status = "SUCCESS"
        response = client.get(f"/status/{mock_task.id}")
    assert response.status_code == 200
    assert response.json()["task_id"] == "mock-task-id"
    assert response.json()["status"] == "SUCCESS"

@patch("app.api.endpoints.redis_client", mock_redis)
def test_result_endpoint(mock_dependencies):
    # Ensure the key format matches what the actual API uses
    mock_redis.get.side_effect = lambda key: (
        '{"files": [], "summary": {"total_files": 0, "total_issues": 0}}'
        if key == f"task:result:{mock_task.id}" else None
    )

    response = client.get(f"/result/{mock_task.id}")
    assert response.status_code == 200  # Ensure success
    assert "files" in response.json()  # Validate response structure


def test_result_endpoint_missing(mock_dependencies):
    # Simulate missing result
    mock_redis.get.return_value = None

    response = client.get(f"/result/{mock_task.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Result not found."  # Match API response

