import requests
import json

GITHUB_API_BASE_URL = "https://api.github.com/repos/python/cpython"
PR_NUMBER = 129213

def get_pr_metadata(pr_number):
    url = f"{GITHUB_API_BASE_URL}/pulls/{pr_number}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_pr_files(pr_number):
    url = f"{GITHUB_API_BASE_URL}/pulls/{pr_number}/files"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def format_json(data):
    return json.loads(json.dumps(data, indent=4))

def prepare_data(pr_number):
    metadata = get_pr_metadata(pr_number)
    files = get_pr_files(pr_number)
    pr_data = {
        "pr_id": metadata["id"],
        "title": metadata["title"],
        "url": metadata["html_url"],
        "files": [
            {
                "name": file["filename"],
                "status": file["status"],
                "patch": file.get("patch"),
                "raw_url": file["raw_url"],
            }
            for file in files
        ],
    }
    return format_json(pr_data)
