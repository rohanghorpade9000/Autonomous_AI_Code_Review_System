import requests
import json

# Constants
GITHUB_API_BASE_URL = "https://api.github.com/repos/python/cpython"
PR_NUMBER = 129213  # Replace with the pull request number


def get_pr_metadata(pr_number):
    """Fetch metadata of the pull request."""
    url = f"{GITHUB_API_BASE_URL}/pulls/{pr_number}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_pr_files(pr_number):
    """Fetch files changed in the pull request."""
    url = f"{GITHUB_API_BASE_URL}/pulls/{pr_number}/files"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def format_json(data):
    """Format and clean JSON to make it usable."""
    # Serialize to string and then parse it back to ensure it's clean
    return json.loads(json.dumps(data, indent=4))


def prepare_data(pr_number):
    """Prepare data for the agent to process."""
    # Fetch PR metadata
    metadata = get_pr_metadata(pr_number)

    # Fetch files changed in the PR
    files = get_pr_files(pr_number)

    # Organize the data
    pr_data = {
        "pr_id": metadata["id"],
        "title": metadata["title"],
        "url": metadata["html_url"],
        "files": [
            {
                "name": file["filename"],
                "status": file["status"],
                "patch": file.get("patch"),  # Diff of changes
                "raw_url": file["raw_url"],  # Raw content URL
            }
            for file in files
        ],
    }

    return format_json(pr_data)


# Example Usage
if __name__ == "__main__":
    try:
        pr_data = prepare_data(PR_NUMBER)
        with open('structured_pr_data.json', 'w') as json_file:
            json.dump(pr_data, json_file, indent=4)
        print(json.dumps(pr_data, indent=4))  # Pretty print the JSON
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PR data: {e}")