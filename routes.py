# coding: utf-8
from server import app, db, mail, serializer
from flask_mail import Message
from models import User, Device, Area
from flask import render_template, request, url_for, redirect, session, flash, abort, jsonify
from sqlalchemy import exc
import itsdangerous, json
from time import sleep

@app.route('/', methods = ['GET'])
def index():
    if not session.get('loggedIn'):
        return render_template('main.html')
    else:
        return redirect(url_for('dashboard'))
@app.before_first_request
def restrict_admin_url():
    endpoint = 'admin.index'
    url = url_for(endpoint)
    admin_index = app.view_functions.pop(endpoint)

    @app.route(url, endpoint=endpoint)
    def secure_admin_index():
        if not session.get('loggedIn'):
            return abort(404)
        else:
            currentUser = User.query.get(session['currentUserId'])
            if currentUser.isAdmin:
                return admin_index()
            return abort(404)

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
            db.session.close()
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
    try:
        db.session.commit()
        db.session.close()
    except:
        db.session.rollback()
        flash(u'Błąd bazy danych!')
    return redirect(url_for('login'))

@app.route('/passwordreset/<token>', methods = ['GET', 'POST'])
def password_reset_token(token):
    try:
        email = serializer.loads(token, salt='password-reset')
    except itsdangerous.BadSignature:
        return '<h1>Błędny token</h1>'
    if request.method =='GET':
        return render_template('passwordreset.html', token=token)
    if request.form['passwordField'] == request.form['password2Field']:
        userResetPassword = User.query.filter_by(email=email).first()
        userResetPassword.passwordHash = userResetPassword.set_password(request.form['passwordField'])
        try:
            db.session.commit()
            db.session.close()
            flash(u'Hasło zostało zmienione')
        except:
            db.session.rollback()
            flash(u'Błąd bazy danych!')
        return redirect(url_for('logout'))
    else:
        flash(u'Wprowadzone hasła różnią się')
        return render_template('passwordreset.html', token=token)


@app.route('/passwordreset')
def password_reset():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        currentUser = User.query.get(session['currentUserId'])
        email = currentUser.email
        name = currentUser.name
        token = serializer.dumps(email, salt='password-reset')
        msg = Message('Zresetuj hasło', sender='Geoloracja', recipients=[email])
        link = url_for('password_reset_token', token=token, _external=True)
        msg.body = 'Witaj {}!\n\nAby zresetować hasło w systemie Geoloracja kliknij w poniższy link:\n\n {} \n\n Zespół Geoloracja.'.format(name, link)
        mail.send(msg)
        flash(u'Wysłano email z linkiem resetującym hasło')
        session['loggedIn'] = False
        session['currentUserId'] = None
        return redirect(url_for('login'))

@app.route('/mydevices', methods=['GET'])
def mydevices():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        currentUser = User.query.get(session['currentUserId'])
        devices = currentUser.device
        return render_template('mydevices.html', devices=devices)

@app.route('/removedevice/<address>')
def removeDevice(address):
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        currentUser = User.query.get(session['currentUserId'])
        devices = currentUser.device
        for device in devices:
            if device.deviceAddress == address:
                currentUser.device.remove(device)
                try:
                    db.session.delete(device)
                    db.session.commit()
                    flash(u'Usunięto urządzenie '+device.name)
                except:
                    db.session.rollback()
                    flash(u'Błąd bazy danych!')
                return redirect(url_for('mydevices'))
        flash(u'Błędne dane!')
        return redirect(url_for('mydevices'))

@app.route('/newdevice', methods=['GET', 'POST'])
def newdevice():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        if request.method == 'GET':
            return render_template('newdevice.html')
        deviceName = request.form['deviceNameField']
        deviceAddress = request.form['deviceAddressField']
        currentUser = User.query.get(session['currentUserId'])
        if deviceName and deviceAddress:
            newDevice = Device(deviceAddress,deviceName)
            try:
                db.session.add(newDevice)
                currentUser.device.append(newDevice)
                db.session.commit()
            except:
                db.session.rollback()
                flash(u'Błąd bazy danych!')
            return redirect(url_for('mydevices'))
        else:
            flash(u'Pola nie zostały wypełnione')
            return render_template('newdevice.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        currentUser = User.query.get(session['currentUserId'])
        isAdmin = currentUser.isAdmin
        devices = currentUser.device
        return render_template('dashboard.html', admin=isAdmin, devices=devices)


@app.route('/selectarea')
def selectarea():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        currentUser = User.query.get(session['currentUserId'])
        devices = currentUser.device
        return render_template('selectarea.html', devices=devices)

@app.route('/myprofile', methods=['GET'])
def myprofile():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        currentUser = User.query.get(session['currentUserId'])
        details = {}
        details['name'] = currentUser.name
        details['surname'] = currentUser.surname
        details['email'] = currentUser.email
        return render_template('myprofile.html', details=details)

@app.route('/editprofile', methods=['GET', 'POST'])
def editprofile():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        currentUser = User.query.get(session['currentUserId'])
        if request.method == 'GET':
            return render_template('editprofile.html', user=currentUser)
        if request.form['nameField'] == '' and request.form['surnameField'] == '':
            flash(u'Pola sa puste')
            return redirect(url_for('editprofile'))
        if request.form['nameField'] != '' and request.form['surnameField'] != '':
            currentUser.name = request.form['nameField']
            currentUser.surname = request.form['surnameField']
            try:
                db.session.commit()
                flash(u'Zmieniono imie i nazwisko')
            except:
                db.session.rollback()
                flash(u'Błąd bazy danych!')
            return redirect(url_for('editprofile'))
        if request.form['nameField'] != '':
            currentUser.name = request.form['nameField']
            try:
                db.session.commit()
                flash(u'Zmieniono imię')
            except:
                db.session.rollback()
                flash(u'Błąd bazy danych!')
            return redirect(url_for('editprofile'))
        if request.form['surnameField'] != '':
            currentUser.surname = request.form['surnameField']
            try:
                db.session.commit()
                flash(u'Zmieniono nazwisko')
            except:
                db.session.rollback()
                flash(u'Błąd bazy danych!')
            return redirect(url_for('editprofile'))
        return redirect(url_for('editprofile'))


@app.route('/setarea/<deviceName>', methods=['POST'])
def getcoords(deviceName):
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        currentUser = User.query.get(session['currentUserId'])
        devices = currentUser.device
        content = request.form
        coordinatesString = ''
        for items in content:
            coordinatesString = items
        for device in devices:
            if device.name == deviceName:
                newArea = Area(coordinatesString)
                try:
                    db.session.add(newArea)
                    userDevice = Device.query.filter_by(name=deviceName).first()
                    userDevice.area.append(newArea)
                    db.session.commit()
                except:
                    db.session.rollback()
                    flash(u'Błąd bazy danych!')
        flash(u'Ustawiono nowy obszar dla urzadzenia '+deviceName)
        return 'OK'


@app.route('/logout')
def logout():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    else:
        session['loggedIn'] = False
        session['currentUserId'] = None
        return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/testnotif')
def notif():
    return '<script>var e = new Notification("Geoloracja", { body: "Twoje urządzenie opuściło obszar!", icon: "http://localhost:5000/static/images/geoloracja_logo.png" });</script>'

#Thread for getting live messages from devices

# thread = Thread()
# thread_stop_event = Event()
#
# class Lora(Thread):
#     def __init__(self):
#         self.delay = 5
#         super(Lora, self).__init__()
#
#     def lora_listener(self):
#         print("Started listening...")
#         app_id = "geoloracja"
#         access_key = "ttn-account-v2.cxnYXM8WxBx65iUHiI8KqNcpFFmGKtud5jEU-TtaiAo"
#         handler = ttn.HandlerClient(app_id, access_key)
#         while not thread_stop_event.isSet():
#             mqtt_client = handler.data()
#             mqtt_client.set_uplink_callback(self.uplink_callback)
#             mqtt_client.connect()
#             sleep(self.delay)
#             mqtt_client.close()
#
#     def uplink_callback(self, msg, client):
#         print(msg.payload_fields)
#         socketio.emit('abc', {'msg': msg.payload_fields})
#
#     def run(self):
#         self.lora_listener()

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
