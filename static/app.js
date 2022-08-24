document.addEventListener('DOMContentLoaded', function () {

    const map = L.map('map').setView([62.250846, 25.768910], 7);

    navigator.geolocation.getCurrentPosition(position => {
        map.panTo([position.coords.latitude, position.coords.longitude]);
    });

    const closeup = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    });

    closeup.addTo(map);

    const artistic = L.tileLayer('http://{s}.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg', {
        attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
        subdomains: 'abcd',
        minZoom: 3,
        maxZoom: 13
    });

    artistic.addTo(map);

    fetch('./data', { method: 'get' })
        .then(response => response.json())
        .then(data => {
            let icon = L.icon({
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                iconUrl: '/static/burger32.png'
            });
            L.geoJson([data], {
                style: function (feature) {
                    return feature.properties && feature.properties.style;
                },
                onEachFeature: function(feature, layer) {
                    layer.bindPopup(timeTable(feature.properties));
                },
                pointToLayer: function (feature, latlng) {
                    return L.marker(latlng, {icon: icon});
                }
            }).addTo(map);
        });

});

function fixTime(t) {
    var m;
    if ((m = /([0-9]{2}):00/.exec(t)) != null) {
        return m[1];
    } else {
        return t;
    }
}

function timeTable(properties) {
    var ret = properties.name + ", " + properties.addressLine3 + "<br/>";
    /*
    ret += '<table><tr>';
    for (var i = 0; i < 7; i++) {
        ret += '<td>';
        var hours = properties.openhours[i].split(',');
        if (hours[0] === 'always') {
            ret += '24/7';
        } else {
            ret += fixTime(hours[0]) + '-' + fixTime(hours[1]);
        }
        ret += '</td>';
    }
    ret += '</tr></table>';
    ret += properties.remarkhours;
    */
    return ret;
}
