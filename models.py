from server import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    isAdmin = db.Column(db.Boolean)

class Device(db.Model):
    id = db.Column(db.String(50), primary_key = True)
    name = db.Column(db.String(50))
    ownerId = db.Column(db.Integer)
