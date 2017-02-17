/*global define, depot, google */
define([], function () {

    var initialize = function () {
        var mapOptions = {
            zoom: 14,
            center: new google.maps.LatLng(47.3833419, 8.5144495)
        };
        var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
        var createDepotMap = function (depot) {
            var depotMarker = new google.maps.Marker({
                position: new google.maps.LatLng(depot.latitude, depot.longitude),
                map: map,
                title: depot.name
            });
        };
        var geocoder = new google.maps.Geocoder();

        for (var i = 0; i < locos.length; i++) {
            var string = locos[i];
            var addLoco = function (position) {
                var locoMarker = new google.maps.Circle({
                    strokeColor: '#4c9434',
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: '#4c9434',
                    fillOpacity: 1,
                    map: map,
                    center: position,
                    radius: 25
                });
            }
            if (localStorage.getItem(string + "lat") && localStorage.getItem(string + "lng")) {
                addLoco({
                    lat: parseFloat(localStorage.getItem(string + "lat")),
                    lng: parseFloat(localStorage.getItem(string + "lng"))
                });
            } else {
                geocoder.geocode({'address': locos[i]}, function (results, status) {
                    if (status === google.maps.GeocoderStatus.OK) {
                        addLoco(results[0].geometry.location);
                        localStorage.setItem(string + "lat", results[0].geometry.location.lat());
                        localStorage.setItem(string + "lng", results[0].geometry.location.lng());
                    }
                });
            }
        }

        for (var i = 0; i < depots.length; i++) {
            if (depots[i].latitude) {
                createDepotMap(depots[i]);
            }
        }

        $(window).resize(function () {
            google.maps.event.trigger(map, 'resize');
        });
        google.maps.event.trigger(map, 'resize');
    };
    var timeout = setInterval(function () {
        if (window.google) { // wait until google is loaded
            clearInterval(timeout);
            initialize();
        }
    }, 100)
});