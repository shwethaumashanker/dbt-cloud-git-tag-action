# stdlib
import logging
import os
import sys
from typing import Dict

# third party
import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# dbt Cloud Env Vars
TOKEN = os.getenv("INPUT_DBT_CLOUD_SERVICE_TOKEN", None)
ACCOUNT_ID = os.getenv("INPUT_DBT_CLOUD_ACCOUNT_ID", None)
PROJECT_ID = os.getenv("INPUT_DBT_CLOUD_PROJECT_ID", None)
ENV_ID = os.getenv("INPUT_DBT_CLOUD_ENVIRONMENT_ID", None)
HOST = os.getenv("INPUT_DBT_CLOUD_HOST", "cloud.getdbt.com")

# Github Env Vars
GITHUB_REF = os.getenv("GITHUB_REF", None)


def make_request(path: str, *, method="GET", **kwargs) -> Dict:
    url = f"https://{HOST}/{path}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.request(method, url, headers=headers, **kwargs)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    # Get the latest tag
    tag = GITHUB_REF.split("/")[-1]
    path = f"api/v3/accounts/{ACCOUNT_ID}/projects/{PROJECT_ID}/environments/{ENV_ID}/"

    # Log the extracted tag
    logger.info(f"Using tag: {tag}")

    # Retrieve the environment to update
    environment = make_request(path)["data"]

    # Update the environment with the custom branch
    environment["custom_branch"] = tag
    environment["use_custom_branch"] = True

    # Remove credentials
    environment["credentials"] = None

    # Log the env
    logger.info(f"env: {environment}")
    
    # Update the environment
    try:
        response = make_request(path, method="POST", json=environment)
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        logger.error(f"Response content: {e.response.content}")
        sys.exit(1)


    if response["status"]["code"] == 200:
        sys.exit(0)

    logger.error(response["status"])
    sys.exit(1)
