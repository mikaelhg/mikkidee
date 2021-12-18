#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates
import uvicorn
import requests


templates = Jinja2Templates(directory='templates')
app = Starlette(debug=True)
app.mount('/static', StaticFiles(directory='static'), name='static')


def fetch_restaurants() -> dict:
    url = 'https://www.mcdonalds.com/googleappsv2/geolocation'
    params = {
        'method': 'searchLocation',
        'latitude': '63.87825211388366',
        'longitude': '27.004699026773824',
        'radius': '5000',
        'maxResults': '1000',
        'country': 'fi',
        'language': 'fi-fi',
        'showClosed': '',
        'hours24Text': 'Open 24 hr',
    }
    headers = {
        'Referer': 'https://www.mcdonalds.com/fi/fi-fi/palvelut/ravintolahaku.html',
        "accept": "*/*",
        "accept-language": "en-FI,en-US;q=0.9,en;q=0.8,fi-FI;q=0.7,fi;q=0.6,en-GB;q=0.5",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"96\", \"Google Chrome\";v=\"96\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
    }
    result = requests.get(url, params=params, headers=headers, timeout=3)
    result.raise_for_status()
    return result.json()


def convert_geojson(restaurants: dict) -> dict:
    features = []
    for restaurant in restaurants["features"]:
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': restaurant['geometry']['coordinates']
            },
            'properties': restaurant['properties']
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
        with open('mcd.json', 'rb') as f:
            restaurants = json.load(f)
    geojson = convert_geojson(restaurants)
    return JSONResponse(geojson)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=5000)
