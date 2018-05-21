import paho.mqtt.client as paho
import json
from train import loadClassifier

def on_connect(client, userdata, flags, rc):
    print("CONNACK received with code %d." % (rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))
    
 
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    gateways = {}
    for g in data['metadata']['gateways']:
        gateways[g['gtw_id']] = g['rssi']
        
    predict_in_area(gateways)

def predict_in_area(gateways):
    #gateways['eui-1234567891abcdef'] = -100
    try:
        sample = [[gateways['eui-1234567890abcdef'], gateways['eui-1234567891abcdef'], gateways['eui-1234567892abcdef']]]
    except:
        print('not enough gateways! %s' % gateways)
        return 
    print ("predict for %s: %s" % (gateways, classifier.predict(sample)))


classifier = loadClassifier("classifier.pickle.gzip") 

client = paho.Client()

client.username_pw_set("geoloracja", "ttn-account-v2.g5cvI9Hj069aVpFgaJlL89LzWYBmUdpjHJ8lUVwStt0")
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("eu.thethings.network" , 1883)

client.subscribe("+/devices/+/up")
 
client.loop_forever()