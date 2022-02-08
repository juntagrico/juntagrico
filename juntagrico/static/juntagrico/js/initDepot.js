/*global define */
define([], function () {

    const markers = map_with_markers([JSON.parse(document.getElementById('depot_data').textContent)])
    if(markers[0])
        markers[0].openPopup();

});