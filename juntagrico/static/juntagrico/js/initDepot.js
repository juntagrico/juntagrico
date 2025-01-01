/*global define */
define([], function () {

    map_with_markers([JSON.parse(document.getElementById('depot_data').textContent)], 0)

});