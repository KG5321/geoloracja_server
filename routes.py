# coding: utf-8
from server import app, db, socketio
from models import User
from flask import render_template, request, url_for, redirect, session, flash, abort
from sqlalchemy import exc
from threading import Thread, Event
import ttn
from time import sleep

thread = Thread()
thread_stop_event = Event()

class Lora(Thread):
    def __init__(self):
        self.delay = 10
        super(Lora, self).__init__()

    def lora_listener(self):
        print("Started listening...")
        app_id = "geoloracja"
        access_key = "ttn-account-v2.cxnYXM8WxBx65iUHiI8KqNcpFFmGKtud5jEU-TtaiAo"
        handler = ttn.HandlerClient(app_id, access_key)
        while not thread_stop_event.isSet():
            print("Loop is working")
            mqtt_client = handler.data()
            mqtt_client.set_uplink_callback(self.uplink_callback)
            mqtt_client.connect()
            sleep(self.delay)
            mqtt_client.close()

    def uplink_callback(self, msg, client):
        print("test", msg)
        socketio.emit('abc', msg)

    def run(self):
        self.lora_listener()



@app.route('/', methods = ['GET'])
def index():
    if not session.get('loggedIn'):
        return render_template('main.html')
    else:
        return redirect(url_for('dashboard'))

@socketio.on('connect')
def test_connect():
    global thread
    print('Client connected')
    if not thread.isAlive():
        print("Starting thread")
        thread = Lora()
        thread.start()

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

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
        session['currentUserId'] = findUser.id
        return redirect(url_for('dashboard'))
    flash(u'Dane są niepoprawne. Spróbuj jeszcze raz.')
    return redirect(url_for('login'))

@app.route('/testing')
def testing():
    return render_template('test.html')

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
        print('Current user: '+currentUser.name+' '+currentUser.surname)
        return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session['loggedIn'] = False
    session['currentUserId'] = None
    return redirect(url_for('index'))
