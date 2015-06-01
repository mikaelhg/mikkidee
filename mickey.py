#!/usr/bin/python2
# -*- coding: utf-8 -*-

import urllib2
from flask import *
from flask.ext.assets import Environment
from werkzeug.contrib.fixers import ProxyFix

country_urls = {
    'fi': 'http://apps.mcdonalds.se/fi/stores.nsf/markers?ReadForm',
    'se': 'http://apps.mcdonalds.se/sweden/restSite.nsf/markers?ReadForm'
}

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
assets = Environment(app)
assets.url = app.static_url_path


@app.route('/')
def hello():
    return render_template('index.jinja2')


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
