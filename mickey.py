#!/usr/bin/python2
# -*- coding: utf-8 -*-

from __future__ import print_function
from future.utils import iteritems

from flask import *
from flask_assets import Environment
from geoip2.errors import AddressNotFoundError
from werkzeug.contrib.fixers import ProxyFix
import geoip2.database
import requests

country_urls = {
    'fi': 'http://apps.mcdonalds.se/fi/stores.nsf/markers?ReadForm',
    'se': 'http://apps.mcdonalds.se/sweden/restSite.nsf/markers?ReadForm'
}

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
assets = Environment(app)
assets.url = app.static_url_path

reader = geoip2.database.Reader('GeoLite2-City.mmdb')


def model_geo(ip):
    try:
        city = reader.city(ip)
        return json.dumps({'latitude': city.location.latitude, 'longitude': city.location.longitude})
    except AddressNotFoundError:
        return json.dumps({"latitude": 60.1756, "longitude": 24.9342})


@app.route('/')
def hello():
    return render_template('index.jinja2', geo=model_geo(request.remote_addr))


@app.route('/data')
def data():
    features = []
    for country, url in iteritems(country_urls):
        try:
            response = requests.get(url)
            response.raise_for_status()
            mcd_json = response.json()
        except requests.HTTPError:
            with open('%s_backup.json' % country, 'r') as f:
                mcd_json = json.loads(str(f.read()), encoding='utf-8')
        for m in mcd_json["markers"]:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [float(m['lng']), float(m['lat'])]
                },
                'properties': {key: value for (key, value) in iteritems(m)}
            })
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    return jsonify(geojson)


if __name__ == "__main__":
    app.run(use_debugger=False, debug=True, use_reloader=True, host='0.0.0.0')
