from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from sklearn.ensemble import RandomForestClassifier
import re
import numpy as np
import gzip
import pickle

def isInArea(p, area_points):
    pattern = re.compile("([0-9.]+)")
    numbers = pattern.findall(area_points)
    if len(numbers) % 2 == 1:
        raise Exception("Odd number of parsed coords") 

    pointList = []
    for lat, lng in zip (numbers[::2], numbers[1::2]):
        point = Point(float(lat), float(lng))
        pointList.append(point)

    lat = float(p['lat'])
    lng = float(p['lng'])
    point = Point(lat, lng)
    polygon = Polygon([[p.x, p.y] for p in pointList])

    result = polygon.contains(point)
    return result

"""
mote	time	seqNo	data	lat	lon	alt	packet_id	gateway1	snr1_cB	rssi1_dBm	gateway2	snr2_cB	rssi2_dBm	gateway3	snr3_cB	rssi3_dBm
0       1       2       3       4   5   6   7           8           9       10          11          12      13          14          15      16

z pracy Bartosza Nikodema
L.p Adres Wspolrzedne geograficzne
1 ul. T.Kosciuszki 135 51.099 N, 17.046 E eui-1234567890abcdef
2 ul. Wittiga 8 - dachu domu studenckiego T-19 51.103 N, 17.085 E eui-1234567891abcdef
3 ul. Reja 54-56, dach akademika T-6 51.118 N, 17.058 E eui-1234567892abcdef
"""
def createDataset(fname, area):
    with open(fname, "r") as inf:
        next(inf) # skip first line
        X = [] # dataset
        y = [] # class
        for l in inf:
            l = l.replace(',', '.').split(';')
            record = [l[10], l[13], l[16].strip()] # [rssi1, rssi2, rssi3]
            X.append(record)
            y.append("in" if isInArea({"lat": l[4], "lng": l[5]}, area) else "out")
        return X, y

def trainRandomForest(trainingDataset, targetDataset, numberOfEstimators = 10):
    print ("Number of estimators - " + str( numberOfEstimators))
    classifier = RandomForestClassifier(numberOfEstimators)
    classifier.fit(trainingDataset,targetDataset)
    name = str(numberOfEstimators) + "EstimatorsRandomForest"
    return classifier, name

def dumpClassifier(classifier, fname):
    fp = gzip.open(fname, 'wb') # This assumes that primes.data is already packed with gzip
    pickle.dump(classifier, fp)
    fp.close()

def loadClassifier(fname):
    fp = gzip.open(fname, 'rb') # This assumes that primes.data is already packed with gzip
    classifier = pickle.load(fp)
    fp.close()
    return classifier

if __name__ == "__main__":

    sample_area = "[{lat: 51.11023846371978, lng: 17.05868413282974}, {lat: 51.1084062842131, lng: 17.057611249223783}, {lat: 51.107826977050095, lng: 17.06115176512344}, {lat: 51.1089990561194, lng: 17.0616667492543}]"

    in_area = {"lat": "51.108560", "lng": "17.060121"} # sample known positions
    out_area = {"lat": "51.110584", "lng": "17.060386"} # sample known positions

    dataset_fname = "geo_data.csv"
    classifier_fname = "classifier.pickle.gzip"

    print ("loading from raw file: " + dataset_fname)

    X, y = createDataset(dataset_fname, sample_area)

    print ("creating classifier")

    classifier, name = trainRandomForest(np.array(X), np.array(y))

    dumpClassifier(classifier, classifier_fname)

    print ("classifier dumped")

    sample = [[-121, -12, -121]]

    print ("predict for %s: %s" % (sample, classifier.predict(sample)))
