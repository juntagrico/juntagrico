/*global google */
define([], function () {

    var createDepotOnMap = function (map, name, addr, zip, city, lat, long) {
        var depot = new google.maps.Marker({
            position: new google.maps.LatLng(lat, long),
            map: map,
            title: name
        });
        google.maps.event.addListener(depot, 'click', function () {
            new google.maps.InfoWindow({
                content: "<h1>" + name + "</h1>" + addr + "<br/>" + zip + " " + city
            }).open(map, depot);
        });
    };

    // google map
    var initialize = function () {
        var mapOptions = {
            zoom: 11,
            center: new google.maps.LatLng(47.3825462, 8.4653627)
        };
        var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

        $.each(depots, function (i, depot) {
                createDepotOnMap(map, depot.name, depot.addr_street, depot.addr_zipcode, depot.addr_location, depot.latitude, depot.longitude);
            }
        );
    };

    var calculateDistances = function (member_addr, destinations, depots) {

        // sort the depots for their distance
        var callback = function (response, status) {
            if (status == google.maps.DistanceMatrixStatus.OK) {
                var origins = response.originAddresses;

                for (var i = 0; i < origins.length; i++) {
                    var results = response.rows[i].elements;
                    for (var j = 0; j < results.length; j++) {
                        $("#depot" + depots[j].code).append(" (" + Math.round(results[j].duration.value / 60) + " Minuten zu Fuss)");
                        depots[j].duration = Math.round(results[j].duration.value / 60)
                    }
                }
            }

            // reorder the depots now according to distances
            var $depotOptions = $("#depot");
            var sortedDepots = depots.sort(function (a, b) {
                return a.duration - b.duration;
            });
            $.each(sortedDepots, function (i, d) {
                $("#depot").append($depotOptions.find("#depot" + d.code).addClass("sorted"));
            });
            $depotOptions.find("option").not(".sorted").remove();

        };
        if (window.google) {
            // create the map
            google.maps.event.addDomListener(window, 'load', initialize);

            var service = new google.maps.DistanceMatrixService();
            service.getDistanceMatrix({
                origins: [member_addr],
                destinations: destinations,
                travelMode: google.maps.TravelMode.WALKING,
                unitSystem: google.maps.UnitSystem.METRIC
            }, callback);
        }
    };

    return {
        // needs "#map-canvas" and "#depot" to be present in the dom
        calculate: calculateDistances,
        // creates a tip on the map
        createDepotOnMap: createDepotOnMap
    }
});
