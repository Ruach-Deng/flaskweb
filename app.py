from flask import Flask, render_template, request, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy.orm as so
import sqlalchemy as sa
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_required
from flask_login import UserMixin
# from app.models import User
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, BooleanField, SubmitField
# from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
# from app.forms import RegistrationForm
from flask_login import current_user, login_user
from flask import flash
from flask_login import logout_user


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'app.db')
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
    # Methods to set and check password
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)
    

#Initialize the database and create the user table
with app.app_context():
    db.create_all()

# Define a user loader function to load a user from the database based on their user ID
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




# Registration Form using Flask-WTF
# class RegistrationForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     password2 = PasswordField(
#         'Repeat Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Register')

#     def validate_username(self, username):
#         user = db.session.scalar(sa.select(User).where(
#             User.username == username.data))
#         if user is not None:
#             raise ValidationError('Please use a different username.')

#     def validate_email(self, email):
#         user = db.session.scalar(sa.select(User).where(
#             User.email == email.data))
#         if user is not None:
#             raise ValidationError('Please use a different email address.')
        

# # Login Form using Flask-WTF
# class LoginForm(FlaskForm):
#     username = StringField("Username", validators=[DataRequired(), Length(1, 64)])
#     password = PasswordField("Password", validators=[DataRequired()])
#     remember_me = BooleanField("Remember me")
#     submit = SubmitField("Sign in")



# dictionary to store user and password
#users = {
#    'kunal@gmail.com': '1234',
#    'user2@gmail.com': 'password2'
#}


# Placeholder event data (iterable)

# Define the Event model
class Event(db.Model):
    # Defining all the class variables
    id = db.Column(db.Integer, primary_key=True)
    title: so.Mapped[str] = so.mapped_column(index=True, default="No title")
    date: so.Mapped[datetime] = so.mapped_column(index=True, default=datetime.now)
    location: so.Mapped[str] = so.mapped_column(index=True, default="No Location")
    description: so.Mapped[str] = so.mapped_column(index=True, default="No Description")

    
# Delete these because we are using a database now
# Placeholder event data (iterable)
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
#@app.route('/login', methods=['GET', 'POST'])
#def login():
    
   # if request.method == 'POST':
       # email = request.form.get('email')
       # password = request.form.get('password')
        #print(email, password)

       # if email in users and users[email] == password:
        #    return '<h1>Welcome!!!</h1>'
       # else:
           # return '<h1>Invalid credentials!</h1>'
    #else:
       # return render_template('login.html')


# Combined GET and POST handling for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login started...")
    if current_user.is_authenticated:
        print("User is already authenticated")
        return redirect(url_for('home'))
    if request.method == 'POST':
        user = db.session.scalar(
            sa.select(User).where(User.email == request.form.get('email')))
        if user is None or not user.check_password(request.form.get('password')):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template('login.html', title='Sign In')    
   
    
# Combined GET and POST handling for registration

# use the same for login for registration
# add all the links to connect all the webpages together

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # make sure fields are not empty
        if not email or not password:
            flash("Please fill out all fields.")
            return redirect(url_for("register"))
        
         # check if email already exists
        existing = db.session.scalar(sa.select(User).where(User.email == email))
        if existing:
            flash("Email already registered.")
            return redirect(url_for("login"))

        print(email, password)
        user = User(email=email)
        user.set_password(password)

       
       # Add the new user to the database
        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    
    return render_template('register.html',)

# Logout
# @login_required(), to protect routes that require authentication use it for post event routes
#  as well as managing events

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


# Route to display all events (iterable data)
@app.route('/events', methods=['GET', 'POST'])
def event_list():
    if request.method == "POST":
        obj = Event()
        obj.title = request.form.get('title')

        # convert date string to datetime object
        date_str = request.form.get('date')
        obj.date = datetime.strptime(date_str, "%b %d, %Y")
        # obj.date = request.form.get('date')

        obj.location = request.form.get('location')
        obj.description = request.form.get('description')
        
        db.session.add(obj)
        #Commit chnages to end of the route
        db.session.commit()
        return "Form submitted successfully!"
    
    # redirect to events page after submission - redirect/events

    elif request.method == "GET":
        # Add the contents of the database to the events list
        #Create a database query
        events = db.session.scalars(sa.select(Event))

        #Render the events template with the events data
        return render_template('events.html', events=events)

#Route to post a new event (form handling)

@app.route('/post_event' )
def post_event():
    return render_template('post_event.html')



#     #Create a database query
#     query = sa.select(Event)
#     d = db.session.scalars(query).all()

#     if request.method == 'POST':
#         title = request.form.get('title')
#         date = request.form.get('date')
#         location = request.form.get('location')
#         description = request.form.get('description')

#         # Append new event to list (simulating database save)
#         events.append({
#             'title': title,
#             'date': date,
#             'location': location,
#             'description': description
#         })

#         return redirect(url_for('event_list'))
    
#     #Adding to the database
#     obj = Event()
#     db.session.add(obj)

#     #Commit chnages to end of the route
#     db.session.commit()

#     return render_template('post_event.html', Event = d)
        
if __name__ == '__main__':
    app.run(debug=True)





