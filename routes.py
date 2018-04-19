# coding: utf-8
from server import app, db, socketio, mail, serializer
from flask_mail import Message
from models import User
from flask import render_template, request, url_for, redirect, session, flash, abort
from sqlalchemy import exc
from threading import Thread, Event
import ttn
from time import sleep


@app.route('/', methods = ['GET'])
def index():
    if not session.get('loggedIn'):
        return render_template('main.html')
    else:
        return redirect(url_for('dashboard'))

@socketio.on('connect')
def socket_connect():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        global thread
        print('Client connected')
        if not thread.isAlive():
            print("Starting thread")
            thread = Lora()
            thread.start()

@socketio.on('disconnect')
def socket_disconnect():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
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
        if findUser.isEmailVerified:
            session['loggedIn'] = True
            session['currentUserId'] = findUser.id
            return redirect(url_for('dashboard'))
        flash(u'Email nie został zweryfikowany')
        return redirect(url_for('login'))
    flash(u'Dane są niepoprawne. Spróbuj jeszcze raz.')
    return redirect(url_for('login'))

@app.route('/listener')
def testing():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        return render_template('test.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.form['passwordField'] == request.form['password2Field']:
        email = request.form['emailField']
        name = request.form['nameField']
        newUser = User(request.form['nameField'], request.form['surnameField'], request.form['emailField'], request.form['passwordField'], False, False)
        try:
            db.session.add(newUser)
            db.session.commit()
            token = serializer.dumps(email, salt='email-confirm')
            msg = Message('Zweryfikuj swój email', sender='Geoloracja', recipients=[email])
            link = url_for('confirm_email', token=token, _external=True)
            msg.body = 'Witaj {}!\n\nAby zweryfikować swój email w systemie Geoloracja kliknij w poniższy link:\n\n {} \n\n Zespół Geoloracja.'.format(name, link)
            mail.send(msg)
            return redirect(url_for('login'))
        except exc.IntegrityError as e:
            db.session.rollback()
            flash(u'Użytkownik o podanym emailu już istnieje!')
            return redirect(url_for('register'))
        return redirect(url_for('login'))
    else:
        flash(u'Podane hasła się różnią')
        return render_template('register.html')

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=86400)
    except SignatureExpired:
        return '<h1>Token wygasł!</h1>'
    userVerified = User.query.filter_by(email=email).first()
    userVerified.isEmailVerified = True
    db.session.commit()
    return redirect(url_for('login'))


@app.route('/mydevices', methods=['GET'])
def mydevices():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        return render_template('mydevices.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        currentUser = User.query.get(session['currentUserId'])
        isAdmin = currentUser.isAdmin
        print('Current user: '+currentUser.name+' '+currentUser.surname)
        return render_template('dashboard.html', admin=isAdmin)

@app.route('/myprofile', methods=['GET'])
def myprofile():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        return render_template('myprofile.html')

@app.route('/logout')
def logout():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        session['loggedIn'] = False
        session['currentUserId'] = None
        return redirect(url_for('index'))

#Thread for getting live messages from devices

thread = Thread()
thread_stop_event = Event()

class Lora(Thread):
    def __init__(self):
        self.delay = 5
        super(Lora, self).__init__()

    def lora_listener(self):
        print("Started listening...")
        app_id = "geoloracja"
        access_key = "ttn-account-v2.cxnYXM8WxBx65iUHiI8KqNcpFFmGKtud5jEU-TtaiAo"
        handler = ttn.HandlerClient(app_id, access_key)
        while not thread_stop_event.isSet():
            mqtt_client = handler.data()
            mqtt_client.set_uplink_callback(self.uplink_callback)
            mqtt_client.connect()
            sleep(self.delay)
            mqtt_client.close()

    def uplink_callback(self, msg, client):
        print(msg.payload_fields)
        socketio.emit('abc', {'msg': msg.payload_fields})

    def run(self):
        self.lora_listener()

#Test routes test 123

# @app.route('/testmail', methods=['GET'])
# def testmail():
#     msg = Message('Hello', sender = 'Geoloracja', recipients = ['koniaxd@gmail.com'])
#     msg.body = "This is the email body"
#     mail.send(msg)
#     return 'test mail send'

# @app.route('/makeadmin')
# def makeadmin():
#    user = User.query.get(session['currentUserId'])
#    user.isAdmin = True
#    db.session.commit()
#    return 'You\'re admin now!'
