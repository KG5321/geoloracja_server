from server import app, db
from models import User

@app.route('/', methods = ['GET'])
def index():
    first = User.query.first()
    return '<h1>Hello '+ first.name +'!</h1>'
