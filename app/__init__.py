from crypt import methods
import os
from pdb import post_mortem
from flask import Flask, render_template, request
from dotenv import load_dotenv
from peewee import *
import datetime
from playhouse.shortcuts import model_to_dict

load_dotenv()
app = Flask(__name__)

if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase('file:memory?mode=memory&cache=shared', uri=True)
else:
    # MySQL setup with peewee
    mydb = MySQLDatabase(os.getenv("MYSQL_DATABASE"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            host=os.getenv("MYSQL_HOST"),
            port=3306
    )   

# New DB table
# REST API??
class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = mydb

print(mydb)

mydb.connect()
mydb.create_tables([TimelinePost]) 

# Dictionary holding personal info
mydata = {'malik': {"firstname": "Malik's",
                    "name": "Malik Baker", 
                    "university": "Boston University", 
                    "degree": "BA, Computer Science", 
                    "years": "2020-2024", 
                    "linkedin": "https://www.linkedin.com/in/malbaker/", 
                    "github": "https://www.github.com/malbaker/", 
                    "activities": "Activities: BUILDS (BU Innovation Lab and Design Space)", 
                    "visited": [["USA", [37.09, -95.71]], ["Jamaica", [18.1, -77.29]]], 
                    "skills": ["Java", "Python", "C", "Linux", "Git", "Bash", "HTML", "CSS", "Bash"], 
                    "about": "I am currently a rising Junior at Boston University pursuing my Bachelor's degree in Computer Science. Within the scope of technology, my passions include open-source software, web development and systems engineering. Outside of that I enjoy listening to music, watching movies, playing the guitar, or tinkering with my custom-built PC or keyboard.", 
                    "seal": "boston"}
        }

# Routing data from dictionary to be displayed on landing page
@app.route('/')
def member(member="malik"):
    person = mydata[member]
    return render_template(f'{member}.html',
                            title="MLH Fellow",
                            name=person["name"],
                            university=person["university"],
                            member=member, url=os.getenv("URL"),
                            linkedin=person["linkedin"],
                            github=person["github"],
                            degree=person["degree"],
                            years=person["years"],
                            activities=person["activities"],
                            skills=person["skills"],
                            about=person["about"],
                            seal=person["seal"],
                            firstname=person["firstname"])

# New route for timeline page
@app.route('/timeline')
def timeline():
    return render_template('timeline.html', title='Timeline')

# Basic POST request
@app.route('/api/timeline_post', methods=['POST'])
def post_time_line_post():
    if request.form.get('name') is None or request.form.get('name') == "":
        return "Invalid name", 400
    elif request.form.get('email') is None or request.form.get('email') == "" or "@" not in request.form.get('email'):
        return "Invalid email", 400

    elif request.form.get('content') is None or request.form.get('content') == "":
        return "Invalid content", 400
    
    else:
        name = request.form['name']
        email = request.form['email']
        content = request.form['content']

        timeline_post = TimelinePost.create(name=name, email=email, content=content)
        return model_to_dict(timeline_post)

# Basic GET request
@app.route('/api/timeline_post', methods=['GET'])
def get_time_line_post():
    return {
        'timeline_posts': [
            model_to_dict(p)
            for p in
TimelinePost.select().order_by(TimelinePost.created_at.desc())
        ]
    }

# Get request for specified id
@app.route('/api/timeline_post/<id>', methods=['GET'])
def get_time_line_post_by_id(id):
    p = TimelinePost.get_by_id(id)
    return model_to_dict(p)

@app.route('/api/timeline_post/<id>', methods=['DELETE'])
def delete_time_line_post_by_id(id):
    p = TimelinePost.get_by_id(id)
    p.delete_instance()
    return "Deleted post with id "+str(id)+"\n"
    