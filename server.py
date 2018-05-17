from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from threading import Thread, Event


app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
global thread
thread = Thread()
thread_stop_event = Event()

from routes import *
from lora_connect import Lora

if __name__ == '__main__':
    # Lora thread for monitoring TTN
    if not thread.isAlive():
        print("Starting Lora thread")
        thread = Lora()
        thread.start()
    # port 5000 for local development
    # app.run(host='0.0.0.0', port=80)
    app.run(host='0.0.0.0', port=5000, threaded=True)
