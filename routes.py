# coding: utf-8
from server import app, db
from models import User
from flask import render_template, request, url_for, redirect, session, flash, abort
from sqlalchemy import exc

@app.route('/', methods = ['GET'])
def index():
    if not session.get('loggedIn'):
        return render_template('main.html')
    else:
        return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form['emailField']
    password = request.form['passwordField']
    findUser = User.query.filter_by(email=email).first()
    if findUser is None:
        flash(u'Dane są niepoprawne. Spróbuj jeszcze raz.')
        return redirect(url_for('login'))
    if findUser.is_correct_password(password):
        session['loggedIn'] = True
        session['currentUserId'] = findUser.get_user_id()
        return redirect(url_for('dashboard'))
    flash(u'Dane są niepoprawne. Spróbuj jeszcze raz.')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    print(request.form['passwordField'])
    if request.form['passwordField'] == request.form['password2Field']:
        newUser = User(request.form['nameField'], request.form['surnameField'], request.form['emailField'], request.form['passwordField'], False)
        try:
            db.session.add(newUser)
            db.session.commit()
            return redirect(url_for('login'))
        except exc.IntegrityError as e:
            db.session.rollback()
            flash(u'Użytkownik o podanym emailu już istnieje!')
            return redirect(url_for('register'))
        return redirect(url_for('login'))
    else:
        flash(u'Podane hasła się różnią')
        return render_template('register.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        currentUser = User.query.get(session['currentUserId'])
        return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session['loggedIn'] = False
    session['currentUserId'] = None
    return redirect(url_for('index'))
