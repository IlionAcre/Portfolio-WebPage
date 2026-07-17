from flask import Flask, render_template, request, flash
import data
from flask_mail import Mail, Message
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flask import jsonify, get_flashed_messages
import logging
import os
import secrets

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = ["FLASK_KEY", "MAIL_SERVER", "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_DEFAULT_SENDER", "REFRESH_TOKEN"]
missing_env_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_env_vars:
    raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing_env_vars)}")


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
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'"
    )
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
        skills=data.skill_list,
        projects=data.project_list,
        ico_social=data.icons["social"],
        ico_skill=data.icons["skill"],
        svg_info="http://www.w3.org/2000/svg",
        icons=data.icons,
        **extra,
    )


@app.route("/")
@app.route("/projects")
def home():
    return render_index()


@app.route("/admin/refresh", methods=["POST"])
@csrf.exempt
@limiter.limit("5 per hour")
def refresh_content():
    """Re-fetch skills/projects/icons from S3 without restarting the process.

    Note: with multiple gunicorn workers, this only refreshes the worker
    process that handles the request - hit it a few times (or just wait
    for normal traffic to cycle through workers) to bring all of them
    up to date. There's no shared cache between workers.
    """
    token = request.headers.get("X-Refresh-Token", "")
    if not secrets.compare_digest(token, os.getenv("REFRESH_TOKEN")):
        return jsonify({"status": "error", "message": "Invalid or missing token"}), 403

    try:
        data.load_content()
    except Exception:
        logger.exception("Failed to refresh site content from S3")
        return jsonify({"status": "error", "message": "Refresh failed, see logs"}), 500

    logger.info("Site content refreshed from S3")
    return jsonify({"status": "ok"})


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

    if subject and ("\r" in subject or "\n" in subject):
        flash("Subject cannot contain line breaks. Please remove them and try again.", "error")
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
        logger.info("Contact form message sent (subject=%r)", subject)
    except Exception:
        logger.exception("Failed to send contact form message")
        flash("An unexpected error occurred. Please try again later.", "error")
    return render_index(form_submitted=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)