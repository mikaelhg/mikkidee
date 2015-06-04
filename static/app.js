jQuery( document ).ready(function() {

    var map = L.map('map').setView([62.250846, 25.768910], 7);

    if (typeof geoip2 !== 'undefined') {
        geoip2.city(
            function (loc) { map.panTo([loc.location.latitude, loc.location.longitude]); },
            function () { }
        );
    }

    var osm = L.tileLayer('http://otile{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.jpeg', {
        minZoom: 13,
        maxZoom: 16,
        attribution: 'Tiles Courtesy of <a href="http://www.mapquest.com/">MapQuest</a> &mdash; Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
        subdomains: '1234'
    });

    osm.addTo(map);

    var stamen = L.tileLayer('http://{s}.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg', {
        attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
        subdomains: 'abcd',
        minZoom: 3,
        maxZoom: 13
    });

    stamen.addTo(map);


    $.ajax({ dataType: "json", url: '/data' }).then(
        function(data, status, xhr) {
            L.geoJson([data], {
                style: function (feature) {
                    return feature.properties && feature.properties.style;
                },
                onEachFeature: function(feature, layer) {
                    layer.bindPopup(timeTable(feature.properties));
                },
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, {
                        radius: 8,
                        fillColor: "#ff7800",
                        color: "#000",
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    });
                }
            }).addTo(map);
        },
        function() {}
    );

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
    var ret = properties.address + ", " + properties.city + "<br/>";
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
    return ret;
}
