#!/usr/bin/python3
# -*- coding: utf-8 -*-

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse, JSONResponse
from starlette.templating import Jinja2Templates
import uvicorn
import requests
import json


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
    result = requests.get(url, params=params, headers=headers, timeout=3)
    result.raise_for_status()
    return result.json()


def convert_geojson(input: dict) -> dict:
    features = []
    for m in input["features"]:
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': m['geometry']['coordinates']
            },
            'properties': m['properties']
        })
    return {
        'type': 'FeatureCollection',
        'features': features
    }


@app.route('/')
async def homepage(request):
    context = {'request': request}
    return templates.TemplateResponse('index.html', context)


@app.route('/data')
async def data(request):
    try:
        restaurants = fetch_restaurants()
    except requests.HTTPError:
        with open('mcd.json', 'r') as f:
            restaurants = json.load(f)
    geojson = convert_geojson(restaurants)
    return JSONResponse(geojson)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=5000)
