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
icon_path = os.getenv("ICONS_PATH")

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
PROJECT_GIFS_DIR = os.path.join(STATIC_DIR, "generated", "projects")

icons = {
    "social": {},
    "skill": {},
    "projects": {}
}


def clean_path(raw_svg):
    path_data = re.findall(r'<path[^>]*\sd=[\'"]([^\'"]+)[\'"]', raw_svg, re.DOTALL)

    return path_data


def fetch_data(folder_path):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
    if "Contents" in response:
        for obj in response["Contents"]:
            file_name = obj["Key"]
            if file_name.endswith(".svg"):
                obj_content = s3_client.get_object(Bucket=bucket_name, Key=file_name)["Body"].read().decode('utf-8')
                if "icon" in file_name:
                    icons["social"][file_name.replace(".svg", "").split('/')[-1]] = clean_path(obj_content)
                elif "skill" in file_name:
                    base64_svg = base64.b64encode(obj_content.encode("utf-8")).decode("utf-8")
                    icons["skill"][file_name.replace(".svg", "").split('/')[-1]] = f"data:image/svg+xml;base64,{base64_svg}"
            elif file_name.lower().endswith(".gif"):
                obj_content = s3_client.get_object(Bucket=bucket_name, Key=file_name)["Body"].read()
                project_id = file_name.lower().replace(".gif", "").split("_")[-1]

                os.makedirs(PROJECT_GIFS_DIR, exist_ok=True)
                dest_path = os.path.join(PROJECT_GIFS_DIR, f"{project_id}.gif")
                tmp_path = dest_path + ".tmp"
                with open(tmp_path, "wb") as f:
                    f.write(obj_content)
                os.replace(tmp_path, dest_path)

                icons["projects"][project_id] = f"generated/projects/{project_id}.gif"


try:
    skill_list_raw = s3_client.get_object(Bucket=bucket_name, Key="data/skills.json")["Body"].read().decode("utf-8")
    skill_list = json.loads(skill_list_raw)

    project_list_raw = s3_client.get_object(Bucket=bucket_name, Key="data/projects.json")["Body"].read().decode("utf-8")
    project_list = json.loads(project_list_raw)

    fetch_data("images/")
except Exception:
    logger.exception("Failed to load site content from S3 (bucket=%s). The app cannot start without this data.", bucket_name)
    raise