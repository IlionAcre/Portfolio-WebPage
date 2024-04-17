from flask import Flask, render_template, redirect, url_for, flash
from data import icons, skill_list, project_list

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", 
                           skills=skill_list, 
                           projects=project_list, 
                           ico_social=icons["social"], 
                           ico_skill=icons["skill"],
                           svg_info="http://www.w3.org/2000/svg")

@app.route('/projects')
def projects():
    return render_template('index.html', 
                           anchor='projects',
                           skills=skill_list, 
                           projects=project_list, 
                           ico_social=icons["social"], 
                           ico_skill=icons["skill"],
                           svg_info="http://www.w3.org/2000/svg")

@app.route('/skills')
def skills():
    return render_template('index.html', 
                           anchor='skills',
                           skills=skill_list, 
                           projects=project_list, 
                           ico_social=icons["social"], 
                           ico_skill=icons["skill"],
                           svg_info="http://www.w3.org/2000/svg")

@app.route('/about')
def about():
    return render_template('index.html', 
                           anchor='about',
                           skills=skill_list, 
                           projects=project_list, 
                           ico_social=icons["social"], 
                           ico_skill=icons["skill"],
                           svg_info="http://www.w3.org/2000/svg")

@app.route('/contact')
def contact():
    return render_template('index.html', 
                           anchor='contact',
                           skills=skill_list, 
                           projects=project_list, 
                           ico_social=icons["social"], 
                           ico_skill=icons["skill"],
                           svg_info="http://www.w3.org/2000/svg")

if __name__ == "__main__":
    app.run(port=5500, host="0.0.0.0", debug=True)