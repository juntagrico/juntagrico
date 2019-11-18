/*global define, $, loco_scheine, depots, destinations, google */
define([], function () {

    // preselect depot
    $("#depot").val(depot_id);
    var map = L.map('depot-map').setView([depots[0].latitude, depots[0].longitude], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        {attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'}).addTo(map);

    markers = []
    $.each(depots, function (i, depot) {
                var marker = L.marker([depot.latitude, depot.longitude]).addTo(map);
                marker.bindPopup("<b>" + depot.name + "</b><br/>" +
                        depot.addr_street + "<br/>"
                        + depot.addr_zipcode + " " + depot.addr_location);
                markers.push(marker)
    });
    var group = new L.featureGroup(markers);
    map.fitBounds(group.getBounds(),{padding:[100,100]});

});