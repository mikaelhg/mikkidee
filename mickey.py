#!/usr/bin/python2

import urllib2
from flask import *

html_headers = {
    'Content-Type': 'text/html;charset=UTF-8'
}

json_headers = {
    'Content-Type': 'text/json;charset=UTF-8',
    'Access-Control-Allow-Origin:': '*'
}

#original_json_url = 'http://apps.mcdonalds.se/fi/stores.nsf/markers?ReadForm'
original_json_url = 'https://gist.github.com/mikaelhg/95b134c0c751a4532c01/raw/85d58c7c200404e433040e179f573dac9db65666/mickeys.geojson'

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html'), 200, html_headers


@app.route('/data')
def data():
    mcdata = load_json(original_json_url)
    features = []
    for m in mcdata["markers"]:
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
    return json.dumps(geojson), 200, json_headers


def load_json(url):
    f = urllib2.urlopen(url)
    ret = json.loads(str(f.read()), encoding='utf-8')
    f.close()
    return ret


if __name__ == "__main__":
    app.run(use_debugger=False, debug=True, use_reloader=True, host='0.0.0.0')
