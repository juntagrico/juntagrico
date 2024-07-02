/*global define */
define([], function () {

    const location = JSON.parse(document.getElementById('location_data').textContent)
    if (location.latitude && location.longitude) {
        $('.open-map').on('click', function() {
            let map = $('#location-map')
            if(map.length) {
                map.toggle()
            } else {
                map_with_markers([location], 0)
            }
            return false
        })
    }

    $('#job-subscribe-form').on('submit', function (e) {
        const message = e.originalEvent.submitter.dataset.message;
        if (message)
            return confirm(message);
        return true
    })

});