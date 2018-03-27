from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit



app = Flask(__name__)
app.config.from_pyfile('config.py')
socketio = SocketIO(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)



from routes import *

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5000)
