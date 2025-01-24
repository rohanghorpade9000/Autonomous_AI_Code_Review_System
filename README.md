
# Autonomous Code Review Agent

An AI-powered autonomous code review agent for analyzing GitHub pull requests.

## Overview

This project implements an AI-based system designed to automate the review of GitHub pull requests. The system fetches pull request (PR) data from GitHub repositories, analyzes code changes using an AI agent, and identifies potential issues, such as bugs, style violations, performance concerns, and code quality improvements. This helps developers receive faster and more thorough reviews to enhance code quality and streamline the review process.

## Project Workflow

1. **PR Fetching**: The system fetches metadata and changed files of a pull request from a specified GitHub repository using the GitHub API.
2. **AI-Powered Code Review**: The fetched PR data is sent to an AI agent, which analyzes the code changes for issues such as bugs, stylistic errors, performance problems, and overall code quality. This analysis is powered by the Gemini API.
3. **Task Management**: A Celery-based task queue processes the pull request analysis asynchronously. Task statuses are tracked using Redis as the message broker and result backend.
4. **Results Reporting**: After the analysis is completed, a JSON report is generated, which details the identified issues and provides suggestions for improvement. The results are stored in Redis for retrieval.

## Features

- **Fetch Pull Request Data**: The system automatically fetches pull request metadata (e.g., title, ID, URL) and changed files from the GitHub API.
- **AI Code Review**: Utilizes the Gemini AI model to analyze code changes and detect issues such as style violations, potential bugs, and performance concerns.
- **Async Task Processing**: Uses Celery to handle the background processing of pull request analysis, enabling efficient, non-blocking execution.
- **Task Status & Results**: Provides API endpoints to check the status of analysis tasks and retrieve the final analysis results in a structured JSON format.
- **Structured Output**: Generates a structured JSON report that includes a summary of issues found in the code and detailed suggestions for fixing them.

## Technologies Used

- **Python**: Core language for building the backend system.
- **FastAPI**: Framework used for building the RESTful API endpoints.
- **Celery**: Asynchronous task queue used for background task processing.
- **Redis**: Message broker and backend for Celery task management, also used to store task results.
- **GitHub API**: Used to fetch pull request data and file changes.
- **Gemini API**: AI-powered code review engine that analyzes pull requests for code quality and best practices.
- **Pydantic**: Used for data validation in API requests.
- **Dotenv**: Manages environment variables securely, including the Gemini API key.
- **Pytest**: Testing framework used for running test cases.

## How It Works

### 1. Pull Request Fetching

When a user submits a request to analyze a GitHub pull request, the system fetches metadata and files associated with the pull request from GitHub using the GitHub API. This data includes details like the pull request title, URL, and the changes made to the codebase.

### 2. AI-Powered Code Review

The fetched PR data is passed to an AI agent that uses the Gemini API to analyze the code changes. The AI identifies issues such as:
- Code style inconsistencies
- Bugs and potential errors
- Performance concerns
- Best practices and suggestions for improvement

The result is a detailed JSON report with an analysis of the code, highlighting the problems and suggesting possible fixes.

### 3. Task Management and Reporting

Each analysis task is processed in the background using Celery. The task is queued, and users can check the task status via API endpoints. Once the task completes, the analysis result is stored in Redis and can be retrieved via an API endpoint.

### 4. API Endpoints

- **POST /analyze**: Submits a pull request for analysis by the AI agent.
- **GET /status/{task_id}**: Checks the status of a submitted task.
- **GET /result/{task_id}**: Retrieves the results of a completed task.

