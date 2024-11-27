import os
import json
import boto3
from dotenv import load_dotenv
import base64
import re

load_dotenv()
headers = {
    "Authorization" : os.getenv('PT')
}

s3_client = boto3.client(
    "s3",
    aws_access_key_id = os.getenv("KEY_ID"),
    aws_secret_access_key = os.getenv("ACCESS_KEY"),
    region_name = os.getenv("REGION")
)

bucket_name = os.getenv("BUCKET")
icon_path = os.getenv("ICONS_PATH")

icons = {
    "social": {},
    "skill": {},
    "projects": {}
}


skill_list_raw = s3_client.get_object(Bucket=bucket_name, Key="data/skills.json")["Body"].read().decode("utf-8")
skill_list = json.loads(skill_list_raw)


project_list_raw = s3_client.get_object(Bucket=bucket_name, Key="data/projects.json")["Body"].read().decode("utf-8")
project_list = json.loads(project_list_raw)

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
            elif file_name.lower().endswith(".gif") :
                obj_content = s3_client.get_object(Bucket=bucket_name, Key=file_name)["Body"].read()
                base64_gif = base64.b64encode(obj_content).decode("utf-8")
                icons["projects"][file_name.lower().replace(".gif","").split("_")[-1]] = f"data:image/gif;base64,{base64_gif}"
                

fetch_data("images/")