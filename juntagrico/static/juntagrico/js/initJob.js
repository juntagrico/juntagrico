/*global define */
define([], function () {

    const location = JSON.parse(document.getElementById('location_data').textContent)
    if (location.latitude && location.longitude) {
        $('.open-map').on('click', function() {
            let map = $('#location-map')
            if(map.length) {
                map.toggle()
            } else {
                const markers = map_with_markers([location])
                if(markers[0])
                    markers[0].openPopup()
            }
            return false
        })
    }

});