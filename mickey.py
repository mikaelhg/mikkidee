#!/usr/bin/python2
# -*- coding: utf-8 -*-

import pygeoip
import urllib2
from flask import *
from saferproxyfix import SaferProxyFix

html_headers = {
    'Content-Type': 'text/html;charset=UTF-8'
}

json_headers = {
    'Content-Type': 'text/json;charset=UTF-8',
    'Access-Control-Allow-Origin:': '*'
}

country_urls = {
    'fi': 'http://apps.mcdonalds.se/fi/stores.nsf/markers?ReadForm',
    'se': 'http://apps.mcdonalds.se/sweden/restSite.nsf/markers?ReadForm'
}

gi = pygeoip.GeoIP('GeoLiteCity.dat')

app = Flask(__name__)
app.wsgi_app = SaferProxyFix(app.wsgi_app)


@app.route('/')
def hello():
    # examples - finland: 212.149.200.241, sweden: 78.108.0.5, london: 92.40.254.141
    location = gi.record_by_addr(request.remote_addr)
    if location and location['country_code'] in ('FI', 'SE'):
        model = {'lat': location['latitude'], 'lng': location['longitude']}
    else:
        model = {'lat': 62.250846, 'lng': 25.768910}
    return render_template('index.html', **model), 200, html_headers


@app.route('/data')
def data():
    return jsonify(get_geojson()), 200, json_headers


def get_geojson():
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
    return geojson


def load_json(handle):
    try:
        ret = json.loads(str(handle.read()), encoding='utf-8')
    finally:
        handle.close()
    return ret


if __name__ == "__main__":
    app.run(use_debugger=False, debug=True, use_reloader=True, host='0.0.0.0')
