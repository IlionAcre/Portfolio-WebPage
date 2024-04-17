import os
import requests
from dotenv import load_dotenv

load_dotenv()
headers = {
    "Authorization" : os.getenv('PT')
}
skill_list = requests.get(os.getenv("SP"), headers=headers).json()["skills"]
project_list = requests.get(os.getenv("PP"), headers=headers).json()["projects"]

icon_path = os.getenv("ICONS_PATH")
contents = os.listdir(icon_path)

icons = {
    "social": {},
    "skill": {},
}

def clean_path(raw_svg):
    raw_svg = raw_svg.read().split(">")[1]+">"
    raw_svg = raw_svg.replace('<path d="','').replace('"/>','')
    return raw_svg


for item in contents:
    item_path = os.path.join(icon_path, item)
    if ".svg" in item and "icon" in item:
        if "icon" in item:
            with open(item_path) as svg:
                icons["social"][item.replace(".svg", "")] = clean_path(svg)
        elif "skill" in item:
            with open(item_path) as svg:
                icons["skill"][item.replace(".svg", "")] = clean_path(svg)
    