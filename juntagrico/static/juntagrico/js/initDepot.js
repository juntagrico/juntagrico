/*global define */
define([], function () {

    var markers = map_with_markers(depots)
    if(markers[0])
        markers[0].openPopup();

});