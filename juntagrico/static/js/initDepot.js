/*global define, depot, google */
define([], function () {

    var map = L.map('depot-map').setView([depot.latitude, depot.longitude], 17);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        {attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'}).addTo(map);
    var marker = L.marker([depot.latitude, depot.longitude]).addTo(map);
    marker.bindPopup("<b>" + depot.name + "</b><br/>" +
                        depot.addr_street + "<br/>"
                        + depot.addr_zipcode + " " + depot.addr_location).openPopup();

});