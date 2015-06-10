#!/usr/bin/python2
# -*- coding: utf-8 -*-

import urllib2

from flask import *
from flask.ext.assets import Environment
from geoip2.errors import AddressNotFoundError
from werkzeug.contrib.fixers import ProxyFix
import geoip2.database

country_urls = {
    'fi': 'http://apps.mcdonalds.se/fi/stores.nsf/markers?ReadForm',
    'se': 'http://apps.mcdonalds.se/sweden/restSite.nsf/markers?ReadForm'
}

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
assets = Environment(app)
assets.url = app.static_url_path

reader = geoip2.database.Reader('GeoLite2-City.mmdb')


def model():
    ret = {}
    try:
        city = reader.city(request.remote_addr)
        ret['geo'] = json.dumps({'latitude': city.location.latitude, 'longitude': city.location.longitude})
    except AddressNotFoundError:
        ret['geo'] = json.dumps({"latitude": 60.1756, "longitude": 24.9342})
    return ret


@app.route('/')
def hello():
    return render_template('index.jinja2', **model())


@app.route('/data')
def data():
    features = []
    for country, url in country_urls.iteritems():
        try:
            mcd_json = load_json(urllib2.urlopen(url))
        except (urllib2.HTTPError, urllib2.URLError):
            mcd_json = load_json(open('%s_backup.json' % country, 'r'))
        for m in mcd_json["markers"]:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [float(m['lng']), float(m['lat'])]
                },
                'properties': {key: value for (key, value) in m.iteritems()}
            })
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    return jsonify(geojson)


def load_json(handle):
    try:
        ret = json.loads(str(handle.read()), encoding='utf-8')
    finally:
        handle.close()
    return ret


if __name__ == "__main__":
    app.run(use_debugger=False, debug=True, use_reloader=True, host='0.0.0.0')
