from server import app, db
from models import User
from flask import render_template, request, url_for, redirect, session, flash, abort


@app.route('/', methods = ['GET'])
def index():
    if not session.get('loggedIn'):
        return render_template('main.html')
    else:
        return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/loginpost', methods=['POST'])
def login_post():
    if request.form['passwordField'] == 'asd' and request.form['emailField'] == 'a@a.pl':
        session['loggedIn'] = True
        return redirect(url_for('dashboard'))
    else:
        return 'Error'

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('loggedIn'):
        return redirect(url_for('login_page'))
    else:
        return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session['loggedIn'] = False
    return redirect(url_for('index'))
