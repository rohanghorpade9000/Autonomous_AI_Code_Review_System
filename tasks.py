# tasks.py
from celery import Celery
from github_ import prepare_data  # Import the GitHub data fetcher
from ai_agent import analyze_with_ai  # Import the AI analysis logic

# Initialize Celery
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)


from redis_client import redis_client  # Import your Redis client
import json  # To handle JSON serialization


@celery_app.task(bind=True)
def analyze_pr_task(self, repo_url, pr_number):
    """
    Fetch PR data, analyze it with the AI agent, clean the result, and store it in Redis.
    """
    try:
        # Fetch the PR data
        pr_data = prepare_data(pr_number)

        # Pass the PR data to the AI agent
        ai_result = analyze_with_ai(pr_data)

        # Clean the AI output (remove artifacts and parse to JSON)
        if isinstance(ai_result, str):
            # Remove unwanted formatting artifacts
            cleaned_output = ai_result.replace("```json", "").replace("```", "").strip()

            # Try to parse it into JSON
            try:
                parsed_output = json.loads(cleaned_output)
            except json.JSONDecodeError:
                parsed_output = {"error": "AI returned invalid JSON output", "raw_output": cleaned_output}
        else:
            parsed_output = ai_result  # If already a dictionary, use as is

        # Save the cleaned result in Redis
        redis_client.set(f"task:result:{self.request.id}", json.dumps(parsed_output))  # Store as JSON string
        redis_client.expire(f"task:result:{self.request.id}", 86400)  # Optional: Set TTL for 24 hours

        # Return the cleaned and parsed output
        return parsed_output
    except Exception as e:
        # Handle errors by saving the error in Redis
        error_message = {"error": str(e)}
        redis_client.set(f"task:result:{self.request.id}", json.dumps(error_message))
        redis_client.expire(f"task:result:{self.request.id}", 86400)
        return error_message


