from threading import Thread, Event
from time import sleep, asctime
import ttn
#from server import thread, thread_stop_event

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
            mclient = handler.data()
            mclient.set_uplink_callback(self.uplink_callback)
            mclient.connect()
            sleep(self.delay)
            mclient.close()

    def uplink_callback(self, msg, client):
        print(msg.dev_id)
        print('{{lat: {}, lng: {}}}'.format(msg.payload_fields.latitude, msg.payload_fields.longitude))
        sleep(self.delay)

    def run(self):
        self.uplink_listener()


# Valid payload data for testing uplink
# 00272808080383F448B4C60C1FC10000
