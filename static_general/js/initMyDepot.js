/*global define, depot, google */
define([], function () {

    if (window.google) { // make it bullet proof if google is not available
        var initialize = function () {
            var mapOptions = {
                zoom: 14,
                center: new google.maps.LatLng(depot.latitude, depot.longitude)
            };
            var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
            var createDepotMap = function (name, addr, zip, city, lat, long) {
                var depotMarker = new google.maps.Marker({
                    position: new google.maps.LatLng(lat, long),
                    map: map,
                    title: depot.name
                });
                new google.maps.InfoWindow({
                    content: "<h1>" + name + "</h1>" + addr + "<br/>" + zip + " " + city
                }).open(map, depotMarker);
            };

            if (depot.latitude) {
                createDepotMap(depot.name, depot.addr_street, depot.addr_zipcode, depot.addr_location, depot.latitude, depot.longitude);
            }

            $(window).resize(function () {
                google.maps.event.trigger(map, 'resize');
                console.log("yea")
            });
            google.maps.event.trigger(map, 'resize');
        };
        $(document).ready(initialize);
    }
});