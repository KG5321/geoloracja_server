from server import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import time

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    surname = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    passwordHash = db.Column(db.Binary(60))
    isAdmin = db.Column(db.Boolean, default=False)
    isEmailVerified = db.Column(db.Boolean, default=False)

    def __init__(self, name, surname, email, plaintext_password, isAdmin, isEmailVerified):
        self.name = name
        self.surname = surname
        self.email = email
        self.passwordHash = self.set_password(plaintext_password)
        self.isAdmin = isAdmin
        self.isEmailVerified = isEmailVerified


    def set_password(self, plaintext_password):
         return bcrypt.generate_password_hash(plaintext_password)

    def is_correct_password(self, plaintext_password):
        return bcrypt.check_password_hash(self.passwordHash, plaintext_password)




class Device(db.Model):

    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key = True)
    deviceAddress = db.Column(db.String)
    name = db.Column(db.String)
    currentLat = db.Column(db.Float)
    currentLng = db.Column(db.Float)
    lastUpdate = db.Column(db.Date)

    def __init__(self, deviceAddress, name):
        self.deviceAddress = deviceAddress
        self.name = name


    def set_location(self, currentLat, currentLng):
        self.currentLat = currentLat
        self.currentLng = currentLng
        self.lastUpdate = time.currentUTC()

class UserDevice(db.Model):

    __tablename__ = 'userDevice'

    id = db.Column(db.Integer, primary_key=True)
    deviceId = db.Column(db.Integer)
    userId = db.Column(db.Integer)

    def __init__(self,deviceId, userId):
        self.deviceId = deviceId
        self.userId = userId
