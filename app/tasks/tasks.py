from celery import Celery
from app.services.github import prepare_data
from app.services.ai_agent import analyze_with_ai
from app.utils.redis_client import redis_client
import json

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(bind=True)
def analyze_pr_task(self, repo_url, pr_number):
    try:
        pr_data = prepare_data(pr_number)
        ai_result = analyze_with_ai(pr_data)
        if isinstance(ai_result, str):
            cleaned_output = ai_result.replace("```json", "").replace("```", "").strip()
            try:
                parsed_output = json.loads(cleaned_output)
            except json.JSONDecodeError:
                parsed_output = {"error": "AI returned invalid JSON output", "raw_output": cleaned_output}
        else:
            parsed_output = ai_result
        redis_client.set(f"task:result:{self.request.id}", json.dumps(parsed_output))
        redis_client.expire(f"task:result:{self.request.id}", 86400)
        return parsed_output
    except Exception as e:
        error_message = {"error": str(e)}
        redis_client.set(f"task:result:{self.request.id}", json.dumps(error_message))
        redis_client.expire(f"task:result:{self.request.id}", 86400)
        return error_message
