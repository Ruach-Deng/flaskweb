from flask import Flask, render_template, request, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy.orm as so
import sqlalchemy as sa
from datetime import datetime


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'app.db')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Set a secret key for encrypting session data
app.secret_key = 'my_secret_key'

# dictionary to store user and password
users = {
    'kunal@gmail.com': '1234',
    'user2@gmail.com': 'password2'
}

# Placeholder event data (iterable)

class Event(db.Model):
    # Defining all the class variables
    id = db.Column(db.Integer, primary_key=True)
    title: so.Mapped[str] = so.mapped_column(index=True, default="No title")
    date: so.Mapped[datetime] = so.mapped_column(index=True, default=datetime.now)
    location: so.Mapped[str] = so.mapped_column(index=True, default="No Location")
    description: so.Mapped[str] = so.mapped_column(index=True, default="No Description")

    

events = [
    {
        'title': 'Soccer Night',
        'date': 'Oct 20, 2025',
        'location': 'EMU Turf',
        'description': 'Come show your soccer skills and meet new people.'
    },
    {
        'title': 'Movie Night',
        'date': 'Oct 23, 2025',
        'location': 'University Commons',
        'description': 'Enjoy a movie with free popcorn and snacks!'
    }
]

@app.route("/")
def home():
    # Displays the homepage with categories and a preview of events
    return render_template("home.html", events=events)

# Combined GET and POST handling for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(email, password)

        if email in users and users[email] == password:
            return '<h1>Welcome!!!</h1>'
        else:
            return '<h1>Invalid credentials!</h1>'
    else:
        return render_template('login.html')
    

# Route to display all events (iterable data)
@app.route('/events')
def event_list():
    return render_template('events.html', events=events)

# Route to post a new event (form handling)
@app.route('/post_event', methods=['GET', 'POST'])
def post_event():

    #Create a database query
    query = sa.select(Event)
    d = db.session.scalars(query).all()

    if request.method == 'POST':
        title = request.form.get('title')
        date = request.form.get('date')
        location = request.form.get('location')
        description = request.form.get('description')

        # Append new event to list (simulating database save)
        events.append({
            'title': title,
            'date': date,
            'location': location,
            'description': description
        })

        return redirect(url_for('event_list'))
    
    #Adding to the database
    obj = Event()
    db.session.add(obj)

    #Commit chnages to end of the route
    db.session.commit()

    return render_template('post_event.html', Event = d)
        
if __name__ == '__main__':
    app.run(debug=True)





