# coding: utf-8
from server import app,db, mail
from models import User, Device, Area
from threading import Thread, Event
from time import sleep, asctime
from flask_mail import Message
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import ttn

class Lora(Thread):
    def __init__(self):
        self.delay = 5
        super(Lora, self).__init__()

    def uplink_listener(self):
        print("Uplink listener is running...")
        app_id = "geoloracja"
        access_key = "ttn-account-v2.cxnYXM8WxBx65iUHiI8KqNcpFFmGKtud5jEU-TtaiAo"
        handler = ttn.HandlerClient(app_id, access_key)
        client = handler.data()
        while True:
            client.set_uplink_callback(self.uplink_callback)
            client.connect()
            sleep(self.delay)
            client.close()

    def uplink_callback(self, msg, client):
        self.update_device(msg)

    def update_device(self, msg):
        findDevice = Device.query.filter_by(name=msg.dev_id).first()
        db.session.close()
        if findDevice is not None:
            lat = msg.payload_fields.latitude
            lng = msg.payload_fields.longitude
            if lat != 0 and lng !=0:
                findDevice.set_location(lat, lng)
                print("Location updated")
                try:
                    coords = findDevice.area.all()[0].coordinatesString
                    self.areaCheck(findDevice, coords)
                except IndexError:
                    print('Area not defined yet, no area check')

            else:
                print("No fix")

    def run(self):
        self.uplink_listener()

    def areaCheck(self, device, coordinates):
        coordinatesString = coordinates
        coordinatesString = coordinatesString[2:]
        coordinatesString = coordinatesString[:-2]
        newData = coordinatesString.split('}, {')
        counter = 0
        toRemove = 'latng: '
        table = {ord(char): None for char in toRemove}
        for data in newData:
            newData[counter] = data.translate(table)
            counter = counter + 1
        pointList = []
        for coord in newData:
            coord = coord.split(',')
            point = Point(float(coord[0]), float(coord[1]))
            pointList.append(point)
        lat = float(device.currentLat)
        lng = float(device.currentLng)
        point = Point(lat, lng)
        polygon = Polygon([[p.x, p.y] for p in pointList])
        result = polygon.contains(point)
        if result:
            print('Device in area')
        else:
            print('Device left area, sending notification')
            findUser = User.query.filter(User.device.contains(device))
            user = findUser.all()[0]
            self.sendNotification(user, device)

    def sendNotification(self, user, device):
        email = user.email
        deviceName = device.name
        name = user.name
        lastUpdate = device.lastUpdate
        time = lastUpdate.time().replace(microsecond=0)
        date = lastUpdate.date()
        # link = url_for('dashboard', _external=True)
        msg = Message(u'Twoje urządzenie '+deviceName+u' opuściło wyznaczony obszar!', sender='Geoloracja', recipients=[email])
        msg.body = u'Witaj {}!\n\nZarejestrowaliśmy że twoje urządzenie o nazwie '.format(name)+deviceName+' o godzinie '+str(time)+', dnia '+str(date)+u' opuściło wyznaczony przez Ciebie obszar.\
        \nSprawdź gdzie aktualnie sie znajduje, na naszej stronie. \n\nZespół Geoloracja.'
        with app.app_context():
            mail.send(msg)


# Valid payload data for testing uplink
# 00272808080383F448B4C60C1FC10000
# Random payload
# 00264643463463463463464363460000
