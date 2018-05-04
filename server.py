from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer



app = Flask(__name__)
app.config.from_pyfile('config.cfg')
socketio = SocketIO(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


from routes import *

if __name__ == '__main__':
    #socketio.run(app, host='0.0.0.0', port=80)
    #port 5000 for local development
    socketio.run(app, host='0.0.0.0', port=5000)
