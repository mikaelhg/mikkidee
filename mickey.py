#!/usr/bin/python2

import json, urllib2
import os
from flask import Flask, Response
from flask import jsonify

app = Flask(__name__)

@app.route('/')
def hello():
  f = urllib2.urlopen('http://apps.mcdonalds.se/fi/stores.nsf/markers?ReadForm')
  data = json.loads(str(f.read()), encoding='UTF-8')
  f.close()

  features = []

  for m in data["markers"]:
    features.append(
      { 'type': 'Feature', 
        'geometry': {
          'type': 'Point',
          'coordinates': [float(m['lat']), float(m['lng'])]
        },
        'properties': {
          'title': m['name']
        }
      })

  geojson = {
    'type': 'FeatureCollection',
    'features': features
  }

  return Response(response=json.dumps(geojson), status=200, mimetype="text/json")


if __name__ == "__main__":
    app.run(use_debugger=False, debug=True, use_reloader=True, host='0.0.0.0')
