import os
import json
import logging
import boto3
from dotenv import load_dotenv
import base64
import re

load_dotenv()
logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = ["KEY_ID", "ACCESS_KEY", "REGION", "BUCKET"]
missing_env_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_env_vars:
    raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing_env_vars)}")

s3_client = boto3.client(
    "s3",
    aws_access_key_id = os.getenv("KEY_ID"),
    aws_secret_access_key = os.getenv("ACCESS_KEY"),
    region_name = os.getenv("REGION")
)

bucket_name = os.getenv("BUCKET")

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
PROJECT_GIFS_DIR = os.path.join(STATIC_DIR, "generated", "projects")
OPTIMIZED_PROJECTS_DIR = os.path.join(STATIC_DIR, "optimized_projects")

icons = {
    "social": {},
    "skill": {},
    "projects": {}
}
skill_list = []
project_list = []


def clean_path(raw_svg):
    path_data = re.findall(r'<path[^>]*\sd=[\'"]([^\'"]+)[\'"]', raw_svg, re.DOTALL)

    return path_data


def fetch_data(folder_path, target_icons):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
    if "Contents" in response:
        for obj in response["Contents"]:
            file_name = obj["Key"]
            if file_name.endswith(".svg"):
                obj_content = s3_client.get_object(Bucket=bucket_name, Key=file_name)["Body"].read().decode('utf-8')
                if "icon" in file_name:
                    target_icons["social"][file_name.replace(".svg", "").split('/')[-1]] = clean_path(obj_content)
                elif "skill" in file_name:
                    base64_svg = base64.b64encode(obj_content.encode("utf-8")).decode("utf-8")
                    target_icons["skill"][file_name.replace(".svg", "").split('/')[-1]] = f"data:image/svg+xml;base64,{base64_svg}"
            elif file_name.lower().endswith(".gif"):
                project_id = file_name.lower().replace(".gif", "").split("_")[-1]

                # Prefer a pre-optimized WebP baked into the image/repo (see
                # scripts/optimize_project_gifs.py) over fetching+writing the
                # raw GIF - skips both the download and any runtime encoding.
                optimized_path = os.path.join(OPTIMIZED_PROJECTS_DIR, f"{project_id}.webp")
                if os.path.exists(optimized_path):
                    target_icons["projects"][project_id] = f"optimized_projects/{project_id}.webp"
                    continue

                obj_content = s3_client.get_object(Bucket=bucket_name, Key=file_name)["Body"].read()

                os.makedirs(PROJECT_GIFS_DIR, exist_ok=True)
                dest_path = os.path.join(PROJECT_GIFS_DIR, f"{project_id}.gif")
                tmp_path = dest_path + ".tmp"
                with open(tmp_path, "wb") as f:
                    f.write(obj_content)
                os.replace(tmp_path, dest_path)

                target_icons["projects"][project_id] = f"generated/projects/{project_id}.gif"


def load_content():
    """(Re)load skill_list, project_list, and icons from S3.

    Rebuilds icons from scratch each call so a removed S3 object doesn't
    leave a stale entry behind. Only affects the process it runs in - see
    the /admin/refresh route docstring for the multi-worker caveat.
    """
    global skill_list, project_list, icons

    skill_list_raw = s3_client.get_object(Bucket=bucket_name, Key="data/skills.json")["Body"].read().decode("utf-8")
    new_skill_list = json.loads(skill_list_raw)

    project_list_raw = s3_client.get_object(Bucket=bucket_name, Key="data/projects.json")["Body"].read().decode("utf-8")
    new_project_list = json.loads(project_list_raw)

    new_icons = {"social": {}, "skill": {}, "projects": {}}
    fetch_data("images/", new_icons)

    skill_list = new_skill_list
    project_list = new_project_list
    icons = new_icons


try:
    load_content()
except Exception:
    logger.exception("Failed to load site content from S3 (bucket=%s). The app cannot start without this data.", bucket_name)
    raise