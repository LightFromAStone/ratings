"""Movie Ratings."""

import email
from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')


@app.route('/login', methods=['GET'])
def show_login():
    """Show Log In Form"""
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def process_login():
    """Logs a user in"""
    
    email = request.form['email']
    password = request.form['password']
    message = 'Email not found'
    
    user = User.query.filter_by(email=email).first()
    if user:
        if user.password == password:
            session['logged_in_user_id'] = user.user_id
            flash('Login Successfull')
            return redirect('/')
        else:
            message = 'Incorrect Password!'
            
    flash(message)
    return redirect('/login')


@app.route("/logout")
def process_logout():
    """Logs user out of site if logged in"""
    
    if session.get('logged_in_user_id'):
        del session['logged_in_user_id']
        flash('Logged out')
        
    return redirect('/')


@app.route('/register', methods=['GET'])
def show_register():
    """Show register form"""
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register_user():
    """Adds user to database if doesn't already exist"""
    
    email = request.form['email']
    password = request.form['password']
    age = request.form['age']
    zipcode = request.form['zipcode']
    
    user = User.query.filter_by(email=email).first()
    if user:
        flash('User already exists')
        return redirect('/register')
    else:
        user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(email=email, password=password).one()
        session['logged_in_user_id'] = user.user_id
        flash('Registered Successfully')
    
    return redirect('/')


@app.route('/users')
def user_list():
    """Show list of users"""
    
    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/users/<user_id>')
def show_user(user_id):
    """Shows page of a particular user"""
    
    user = User.query.filter_by(user_id=user_id).one()
    user.email = ''
    user.password = ''
    ratings = Rating.query.filter_by(user_id=user_id).join(Movie).order_by(Movie.title).all()
    return render_template('user.html', user=user, ratings=ratings)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5005, host='0.0.0.0')
