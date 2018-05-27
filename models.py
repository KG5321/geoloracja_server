from server import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from datetime import datetime

userDevice = db.Table('userDevice',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('device_id', db.Integer, db.ForeignKey('devices.id'))
)

deviceArea = db.Table('deviceArea',
    db.Column('device_id', db.Integer, db.ForeignKey('devices.id')),
    db.Column('area_id', db.Integer, db.ForeignKey('areas.id'))
)

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    surname = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    passwordHash = db.Column(db.Binary(60))
    phone = db.Column(db.String)
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
    name = db.Column(db.String, unique=True)
    currentLat = db.Column(db.Float)
    currentLng = db.Column(db.Float)
    lastUpdate = db.Column(db.DateTime)
    status = db.Column(db.Boolean, default=False)
    users = db.relationship('User', secondary=userDevice, backref=db.backref('device', lazy='dynamic'))

    def __init__(self, deviceAddress, name):
        self.deviceAddress = deviceAddress
        self.name = name


    def set_location(self, currentLat, currentLng):
        self.currentLat = currentLat
        self.currentLng = currentLng
        self.lastUpdate = datetime.now()
        db.session.commit()


class Area(db.Model):

    __tablename__ = 'areas'

    id = db.Column(db.Integer, primary_key=True)
    coordinatesString = db.Column(db.String)
    devices = db.relationship('Device', secondary=deviceArea, backref=db.backref('area', lazy='dynamic'))

    def __init__(self,coordinatesString):
        self.coordinatesString = coordinatesString
