#!/usr/bin/python3
# -*- coding: utf-8 -*-

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse, JSONResponse
from starlette.templating import Jinja2Templates
import uvicorn
import requests
import json


_URL='https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=60.16985569999999&longitude=24.9383791&radius=2500&maxResults=2500&country=fi&language=fi-fi&showClosed=&hours24Text=Open%2024%20hr'
_REF='https://www.mcdonalds.com/fi/fi-fi/palvelut/ravintolahaku.html'


templates = Jinja2Templates(directory='templates')

app = Starlette(debug=True)
app.mount('/static', StaticFiles(directory='static'), name='static')


def fetch_restaurants():
    url = 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do'
    params = {
        'method': 'searchLocation',
        'latitude': '63.87825211388366',
        'longitude': '27.004699026773824',
        'radius': '5000',
        'maxResults': '1000',
        'country': 'fi',
        'language': 'fi-fi',
        'showClosed': '',
        'hours24Text': 'Open 24 hr'
    }
    headers = {
        'Referer': 'https://www.mcdonalds.com/fi/fi-fi/palvelut/ravintolahaku.html'
    }
    result = requests.get(url, params=params, headers=headers)
    result.raise_for_status()
    return result.json()


@app.route('/')
async def homepage(request):
    context = {'request': request}
    return templates.TemplateResponse('index.html', context)


@app.route('/data')
async def data(request):
    features = []
    try:
        mcd_json = fetch_restaurants()
    except requests.HTTPError:
        with open('mcd.json', 'r') as f:
            mcd_json = json.load(f)
    for m in mcd_json["features"]:
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': m['geometry']['coordinates']
            },
            'properties': m['properties']
        })
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    return JSONResponse(geojson)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=5000)
