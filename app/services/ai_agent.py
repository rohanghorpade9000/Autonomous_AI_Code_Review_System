from crewai import Agent, Crew, Process, Task, LLM
import json
import os
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')

if not gemini_api_key:
    raise ValueError("Gemini API key not found.")

def analyze_with_ai(pr_data):
    code_reviewer_agent = Agent(
        role="Code Review Expert",
        goal=f"Analyze pull request changes from {pr_data} and identify issues",
        backstory="""You are a highly experienced software engineer specializing in code reviews.""",
        llm=LLM(
            model="gemini/gemini-1.5-flash",
            temperature=0.5,
        ),
        allow_delegation=False,
        verbose=True,
    )

    task_review_pull_request = Task(
        name="Analyze Pull Request",
        description=f"Analyze the provided pull request code changes from {pr_data} and generate a JSON output detailing identified issues and a summary.",
        agent=code_reviewer_agent,
        expected_output="""Provide a detailed JSON response in this format:
{
    "files": [
        {
            "name": "<FILE_NAME>",
            "issues": [
                {
                    "type": "<ISSUE_TYPE>",
                    "line": <LINE_NUMBER>,
                    "description": "<DESCRIPTION>",
                    "suggestion": "<SUGGESTION>"
                }
            ]
        }
    ],
    "summary": {
        "total_files": <TOTAL_FILES>,
        "total_issues": <TOTAL_ISSUES>,
        "critical_issues": <CRITICAL_ISSUES>
    }
}""",
        input_data={
            "pull_request_data": pr_data
        },
    )

    crew = Crew(
        agents=[code_reviewer_agent],
        tasks=[task_review_pull_request],
        process=Process.sequential,
        verbose=True,
    )

    crew_output = crew.kickoff()
    return crew_output.raw
