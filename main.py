from flask import Flask, render_template, request, flash, redirect, url_for
from data import icons, skill_list, project_list
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_KEY')

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

@app.route("/")
def home():
    return render_template("index.html", 
                           skills=skill_list, 
                           projects=project_list, 
                           ico_social=icons["social"], 
                           ico_skill=icons["skill"],
                           svg_info="http://www.w3.org/2000/svg",
                           icons=icons)

@app.route('/projects')
def projects():
    return render_template('index.html', 
                           anchor='projects',
                           skills=skill_list, 
                           projects=project_list, 
                           ico_social=icons["social"], 
                           ico_skill=icons["skill"],
                           svg_info="http://www.w3.org/2000/svg",
                           icons=icons)
    

@app.route("/submit_contact", methods=["POST"])
def submit_contact():
    name = request.form.get("name")
    email = request.form.get("email")
    subject = request.form.get("subject")
    message = request.form.get("emailContent")
    
    
    try:
        msg = Message(
            subject=f"Contact Form: {subject}",
            sender=app.config["MAIL_DEFAULT_SENDER"],
            recipients=[os.getenv('MAIL_DEFAULT_SENDER')]
        )
        msg.body= f"Name: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}"
        mail.send(msg)
        flash("Message sent successfully!", "success")
    except Exception:
        flash("An unexpected error occurred. Please try again later.", "error")
        
    redirect_url = url_for("home") + "#contact"
    return redirect(redirect_url)



if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")