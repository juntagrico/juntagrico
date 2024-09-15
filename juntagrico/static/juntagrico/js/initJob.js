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

    $('#id_slots').on('change', function (e) {
        let $this = $(this)
        let initial = $this.data('initialSlots')
        let selection = parseInt($this.val())
        let subscribing = selection > initial
        let unsubscribing = selection < initial
        $('#unsubscribe_info').toggleClass('d-none', !unsubscribing)
        $('#div_id_message').toggleClass('d-none', !unsubscribing && !subscribing)
        $('#subscribed_info').toggleClass('d-none', unsubscribing || subscribing)
        $('#submit-id-subscribe').toggleClass('d-none', selection === 0 || selection === initial)
        $('#submit-id-unsubscribe').toggleClass('d-none', selection > 0)
    }).change()

});