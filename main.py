from flask import Flask, render_template, request, flash
from data import icons, skill_list, project_list
from flask_mail import Mail, Message
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flask import jsonify, get_flashed_messages
import os

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_KEY')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 86400

csrf = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app)

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)


@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


CONTACT_FIELD_MAX_LENGTHS = {
    "name": 100,
    "email": 254,
    "subject": 150,
    "emailContent": 5000,
}


def render_index(**extra):
    return render_template(
        "index.html",
        skills=skill_list,
        projects=project_list,
        ico_social=icons["social"],
        ico_skill=icons["skill"],
        svg_info="http://www.w3.org/2000/svg",
        icons=icons,
        **extra,
    )


@app.route("/")
def home():
    return render_index()

@app.route('/projects')
def projects():
    return render_index()


@app.route("/submit_contact", methods=["POST"])
@limiter.limit("5 per minute")
def submit_contact():
    name = request.form.get("name")
    email = request.form.get("email")
    subject = request.form.get("subject")
    message = request.form.get("emailContent")

    for field_name, value, max_length in (
        ("name", name, CONTACT_FIELD_MAX_LENGTHS["name"]),
        ("email", email, CONTACT_FIELD_MAX_LENGTHS["email"]),
        ("subject", subject, CONTACT_FIELD_MAX_LENGTHS["subject"]),
        ("message", message, CONTACT_FIELD_MAX_LENGTHS["emailContent"]),
    ):
        if value and len(value) > max_length:
            flash("Your message is too long. Please shorten it and try again.", "error")
            return render_index(form_submitted=True)

    try:
        msg = Message(
            subject=f"Contact Form: {subject}",
            sender=app.config["MAIL_DEFAULT_SENDER"],
            recipients=[os.getenv('MAIL_DEFAULT_SENDER')]
        )
        msg.body= f"Name: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}"
        mail.send(msg)
        flash("Message sent successfully!", "success")
        print("Message sent")
    except Exception:
        flash("An unexpected error occurred. Please try again later.", "error")
    return render_index(form_submitted=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)