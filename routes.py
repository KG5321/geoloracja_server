from server import app, db
from models import User
from flask import render_template

@app.route('/', methods = ['GET'])
def index():
    first = User.query.first()
    return render_template('index.html')
