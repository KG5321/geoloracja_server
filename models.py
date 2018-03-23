from server import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    surname = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    passwordHash = db.Column(db.Binary(60))
    isAdmin = db.Column(db.Boolean, default=False)

    def __init__(self, name, surname, email, plaintext_password, isAdmin):
        self.name = name
        self.surname = surname
        self.email = email
        self.passwordHash = self.set_password(plaintext_password)
        self.isAdmin = isAdmin


    def set_password(self, plaintext_password):
         return bcrypt.generate_password_hash(plaintext_password)

    def is_correct_password(self, plaintext_password):
        return bcrypt.check_password_hash(self.passwordHash, plaintext_password)

    def get_user_id(self):
        return self.id




class Device(db.Model):
    id = db.Column(db.String(50), primary_key = True)
    name = db.Column(db.String(50))
    ownerId = db.Column(db.Integer)
    currentLat = db.Column(db.Float)
    currentLng = db.Column(db.Float)
