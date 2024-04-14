from flask import Flask, render_template, redirect, url_for, flash
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

SCOPES = ["https://www.googleapis.com/auths/spreadsheets.readonly"]
DATA_ID = "1mP3-B9zY-167B8QsgPrSOL5zafDvDtERxYobg3TQaeE"

credentials = None
if os.path.exists("./db/credentials.json"):
    credits = Credentials.from_authorized_user_file("./db/token.json", SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.flow_client_secrets_file("./db/credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("./db/token.json", "w") as token:
            token.write(credentials.to_json())

        try:
            service = build("sheets", "v4", credentials=credentials)
            sheets = service.spreadsheets()

            result = sheets.values().get(spreadsheetId=DATA_ID, range="Sheet1!A1:C4").execute()

            values = result.get("values", [])

            for row in values:
                print(row)

        except HttpError as error:
            print(error)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/projects')
def projects():
    return render_template('index.html', anchor='projects')

@app.route('/skills')
def skills():
    return render_template('index.html', anchor='skills')

@app.route('/about')
def about():
    return render_template('index.html', anchor='about')

@app.route('/contact')
def contact():
    return render_template('index.html', anchor='contact')

if __name__ == "__main__":
    app.run(port=5500, host="0.0.0.0")