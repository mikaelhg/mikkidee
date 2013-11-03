#!/usr/bin/python2

import json, urllib2
import os
from flask import *

app = Flask(__name__)

@app.route('/')
def hello():
  return render_template('index.html'), 200, {'Content-Type': 'text/html;charset=UTF-8'}

@app.route('/data')
def data():
  f = urllib2.urlopen('http://apps.mcdonalds.se/fi/stores.nsf/markers?ReadForm')
  data = json.loads(str(f.read()), encoding='UTF-8')
  f.close()

  features = []

  for m in data["markers"]:
    features.append(
      { 'type': 'Feature', 
        'geometry': {
          'type': 'Point',
          'coordinates': [float(m['lng']), float(m['lat'])]
        },
        'properties': { key: value for (key, value) in m.iteritems() }
      })

  geojson = {
    'type': 'FeatureCollection',
    'features': features
  }

  return json.dumps(geojson), 200, {'Content-Type': 'text/json', 'Access-Control-Allow-Origin:': '*'}

if __name__ == "__main__":
  app.run(use_debugger=False, debug=True, use_reloader=True, host='0.0.0.0')
