from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from threading import Thread, Event
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
admin = Admin(app, name='Geoloracja Admin', template_mode='bootstrap3')
global thread
thread = Thread()
thread_stop_event = Event()

class GeoloracjaModelView(ModelView):

    def is_accessible(self):
        if session.get('loggedIn'):
            currentUser = User.query.get(session['currentUserId'])
            return currentUser.isAdmin
        return False

    def _handle_view(self, name, *args, **kwargs):
        if not self.is_accessible():
            return abort(403)

from routes import *
from lora_connect import Lora
from models import User, Device, Area

admin.add_view(GeoloracjaModelView(User, db.session))
admin.add_view(GeoloracjaModelView(Device, db.session))
# admin.add_view(GeoloracjaModelView(Area, db.session))


if __name__ == '__main__':
    # Lora thread for monitoring TTN
    if not thread.isAlive():
        print("Starting Lora thread")
        thread = Lora()
        thread.start()
    # port 5000 for local development
    # app.run(host='0.0.0.0', port=80)
    app.run(host='0.0.0.0', port=5000, threaded=True)
