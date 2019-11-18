/*global define, depot, google */
define([], function () {

    var map = L.map('depot-map').setView([depot.latitude, depot.longitude], 17);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        {attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'}).addTo(map);
    var marker = add_marker(depot, map)
    marker.openPopup();

});