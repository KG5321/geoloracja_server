from server import db
from models import User, Device
from threading import Thread, Event
from time import sleep, asctime
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
        while True:
            client = handler.data()
            client.set_uplink_callback(self.uplink_callback)
            client.connect()
            sleep(self.delay)
            client.close()

    def uplink_callback(self, msg, client):
        #print(msg)
        # print(msg.dev_id)
        # print('{{lat: {}, lng: {}}}'.format(msg.payload_fields.latitude, msg.payload_fields.longitude))
        self.update_device(msg)

    def update_device(self, msg):
        findDevice = Device.query.filter_by(name=msg.dev_id).first()
        if findDevice is not None:
            lat = msg.payload_fields.latitude
            lng = msg.payload_fields.longitude
            if lat != 0 and lng !=0:
                findDevice.set_location(lat, lng)
                print("Location updated")
            else:
                print("No fix")

    def run(self):
        self.uplink_listener()


# Valid payload data for testing uplink
# 00272808080383F448B4C60C1FC10000
# Random payload
# 00264643463463463463464363460000
