# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# import os

# SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
# DATA_ID = "1mP3-B9zY-167B8QsgPrSOL5zafDvDtERxYobg3TQaeE"

# credentials = None
# if os.path.exists("token.json"):
#     credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
# else:
#     print("WTF")
# if not credentials or not credentials.valid:
#     if credentials and credentials.expired and credentials.refresh_token:
#         credentials.refresh(Request())
#     else:
#         flow = InstalledAppFlow.from_client_secrets_file(
#           "credentials.json", SCOPES
#       )
#         credentials = flow.run_local_server(port=0)

#         with open("token.json", "w") as token:
#             token.write(credentials.to_json())
# try:
#     service = build("sheets", "v4", credentials=credentials)
#     sheets = service.spreadsheets()

#     result = sheets.values().get(spreadsheetId=DATA_ID, range="Hoja 1!A1:C3").execute()

#     values = result.get("values", [])


    
#     for row in values:
#         print(row)

# except HttpError as error:
#     print(error)


import requests

SKILLS_PATH = "https://api.sheety.co/c9bd17bb67ca968f9ff79282c36661c9/data/skills"
PROJECTS_PATH = "https://api.sheety.co/c9bd17bb67ca968f9ff79282c36661c9/data/projects"

BEARER = "asASDsds!!kjasd//sdSDcvl99//lkSDSDljfdkls8872sdaAS"
headers = {
    "Authorization" : "Bearer asASDsds!!kjasd//sdSDcvl99//lkSDSDljfdkls8872sdaAS"
}

skills = requests.get(SKILLS_PATH, headers=headers)
projects = requests.get(PROJECTS_PATH, headers=headers)


print(skills.text)
print(projects.text)