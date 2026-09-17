import argparse
import json
import logging
import os
import urllib.request
import urllib.error
import boto3
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
SKILLS_FILE = os.path.join(DATA_DIR, "skills.json")
BACKUP_DIR = os.path.join(REPO_ROOT, "data_backup")


def get_s3_client():
    key_id = os.getenv("KEY_ID")
    access_key = os.getenv("ACCESS_KEY")
    region = os.getenv("REGION")
    bucket = os.getenv("BUCKET")

    if not all([key_id, access_key, region, bucket]):
        raise RuntimeError("Missing required AWS credentials in environment (.env).")

    client = boto3.client(
        "s3",
        aws_access_key_id=key_id,
        aws_secret_access_key=access_key,
        region_name=region,
    )
    return client, bucket


def backup_remote_data(s3, bucket):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for key_name, local_name in [("data/projects.json", "projects.json.bak"), ("data/skills.json", "skills.json.bak")]:
        try:
            obj = s3.get_object(Bucket=bucket, Key=key_name)
            content = obj["Body"].read()
            backup_path = os.path.join(BACKUP_DIR, local_name)
            with open(backup_path, "wb") as f:
                f.write(content)
            logger.info("Backed up remote %s to %s", key_name, backup_path)
        except Exception as e:
            logger.warning("Could not backup %s: %s", key_name, e)


def validate_projects(projects):
    if not isinstance(projects, list):
        raise ValueError("projects.json must be a JSON list of project objects.")
    for idx, p in enumerate(projects):
        if "id" not in p:
            raise ValueError(f"Project at index {idx} is missing 'id'.")
        if "title" not in p:
            raise ValueError(f"Project #{p['id']} is missing 'title'.")
        if "description" not in p:
            raise ValueError(f"Project #{p['id']} is missing 'description'.")
        if "links" in p and not isinstance(p["links"], dict):
            raise ValueError(f"Project #{p['id']} 'links' must be an object (key-value dictionary).")


def validate_skills(skills):
    if not isinstance(skills, list):
        raise ValueError("skills.json must be a JSON list of skill objects.")
    for idx, s in enumerate(skills):
        if "name" not in s or "type" not in s:
            raise ValueError(f"Skill at index {idx} is missing 'name' or 'type'.")


def sync_local_data_to_s3(s3, bucket):
    if not os.path.exists(PROJECTS_FILE):
        raise FileNotFoundError(f"Projects file not found: {PROJECTS_FILE}")
    if not os.path.exists(SKILLS_FILE):
        raise FileNotFoundError(f"Skills file not found: {SKILLS_FILE}")

    with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
        projects_data = json.load(f)
    validate_projects(projects_data)

    with open(SKILLS_FILE, "r", encoding="utf-8") as f:
        skills_data = json.load(f)
    validate_skills(skills_data)

    # Upload projects.json
    projects_bytes = json.dumps(projects_data, indent=2).encode("utf-8")
    s3.put_object(
        Bucket=bucket,
        Key="data/projects.json",
        Body=projects_bytes,
        ContentType="application/json",
    )
    logger.info("Uploaded data/projects.json to S3 (%d projects)", len(projects_data))

    # Upload skills.json
    skills_bytes = json.dumps(skills_data, indent=2).encode("utf-8")
    s3.put_object(
        Bucket=bucket,
        Key="data/skills.json",
        Body=skills_bytes,
        ContentType="application/json",
    )
    logger.info("Uploaded data/skills.json to S3 (%d skills)", len(skills_data))


def trigger_refresh(base_url):
    refresh_token = os.getenv("REFRESH_TOKEN")
    if not refresh_token:
        logger.warning("REFRESH_TOKEN not found in .env; skipping remote cache refresh.")
        return

    url = f"{base_url.rstrip('/')}/admin/refresh"
    req = urllib.request.Request(
        url,
        data=b"",
        headers={"X-Refresh-Token": refresh_token},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            logger.info("Triggered server cache refresh at %s: %s", url, data)
    except urllib.error.URLError as e:
        logger.warning("Failed to trigger server cache refresh at %s: %s", url, e)


def main():
    parser = argparse.ArgumentParser(description="Sync local projects.json and skills.json to S3.")
    parser.add_argument(
        "--refresh-url",
        help="Optional base URL of the running web app to trigger /admin/refresh (e.g., http://localhost:8080 or https://falcontreras.com)",
    )
    args = parser.parse_args()

    s3, bucket = get_s3_client()
    logger.info("Backing up remote data from S3 bucket: %s...", bucket)
    backup_remote_data(s3, bucket)

    logger.info("Uploading data from %s to S3...", DATA_DIR)
    sync_local_data_to_s3(s3, bucket)

    if args.refresh_url:
        trigger_refresh(args.refresh_url)

    logger.info("Sync complete! Your projects and skills are updated.")


if __name__ == "__main__":
    main()
