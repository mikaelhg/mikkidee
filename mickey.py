#!/usr/bin/python3
# -*- coding: utf-8 -*-

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse, JSONResponse
from starlette.templating import Jinja2Templates
import uvicorn
import requests


country_urls = {
    'fi': 'http://apps.mcdonalds.se/fi/stores.nsf/markers?ReadForm',
}

_URL='https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=60.16985569999999&longitude=24.9383791&radius=2500&maxResults=2500&country=fi&language=fi-fi&showClosed=&hours24Text=Open%2024%20hr'
_REF='https://www.mcdonalds.com/fi/fi-fi/palvelut/ravintolahaku.html'


templates = Jinja2Templates(directory='templates')

app = Starlette(debug=True)
app.mount('/static', StaticFiles(directory='static'), name='static')


@app.route('/')
async def homepage(request):
    context = {'request': request}
    return templates.TemplateResponse('index.html', context)


@app.route('/data')
async def data(request):
    features = []
    try:
        response = requests.get(_URL, headers={'Referer': _REF})
        response.raise_for_status()
        mcd_json = response.json()
    except requests.HTTPError:
        with open('mcd.json', 'r') as f:
            mcd_json = json.loads(str(f.read()), encoding='utf-8')
    for m in mcd_json["features"]:
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': m['geometry']['coordinates']
            },
#            'properties': {key: value for key, value in m.items()}
            'properties': m['properties']
        })
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    return JSONResponse(geojson)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=5000)
