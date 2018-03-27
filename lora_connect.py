import time
import ttn
from flask import jsonify

app_id = "geoloracja"
access_key = "ttn-account-v2.cxnYXM8WxBx65iUHiI8KqNcpFFmGKtud5jEU-TtaiAo"

def uplink_callback(msg, client):
    print("Received uplink from ", msg.dev_id)
    print(msg)

handler = ttn.HandlerClient(app_id, access_key)

print("Started listening...")

while True:
    mqtt_client = handler.data()
    mqtt_client.set_uplink_callback(uplink_callback)
    mqtt_client.connect()
    time.sleep(1)
    mqtt_client.close()
