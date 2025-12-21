$(function () {
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

    const slots = $('#id_slots')
    const job_extras = $('#job-subscribe-form .checkboxinput')
    slots.on('change', toggle_form_visibility).change()
    job_extras.on('change', toggle_form_visibility)

    function toggle_form_visibility() {
        let initial_slots = slots.data('initialSlots')
        let selection = parseInt(slots.val())
        let subscribing = selection > initial_slots
        let unsubscribing = selection < initial_slots
        let extras_changed = false
        job_extras.each(function() {
            let initial = $(this).data('initialChecked') === "True"
            if (this.checked !== initial) {
                extras_changed = true
                return false
            }
        })
        $('#unsubscribe_info').toggleClass('d-none', !unsubscribing)
        $('#div_id_message').toggleClass('d-none', !unsubscribing && !subscribing && !extras_changed)
        $('#subscribed_info').toggleClass('d-none', unsubscribing || subscribing || extras_changed)
        $('#submit-id-subscribe').toggleClass('d-none', selection === 0 || (selection === initial_slots && !extras_changed))
        $('#submit-id-unsubscribe').toggleClass('d-none', selection > 0)
    }

    // modal to edit assignment
    $('.edit-assignment').on('click', function(event) {
        let url = $(this).data('url')
        let content = $('#edit_assignment_content')
        content.empty()
        $('#edit_assignment_loader').show()
        $('#edit_assignment_modal').modal('show')
        content.load(url, handle_edit_assignment_form(url))
        return false
    })

    function handle_edit_assignment_form(url) {
        let submit_button = $('#edit_assignment_submit')
        return function(response, status, xhr) {
            $('#edit_assignment_loader').hide()
            if (status === 'error') {
                $(this).text(xhr.status + ' ' + xhr.statusText)
                submit_button.prop('disabled', true)
            } else {
                submit_button.prop('disabled', false).attr('formaction', url)
            }
        }
    }

    // open modal to convert to recurring job
    $('.convert-to-recurring-job').on('click', function (event) {
        let modal = $('#convert_to_recurring_job_modal')
        modal.modal('show')
        // re-apply select2 to calculate correct width of fields
        modal.find('.django-select2').not('[name*=__prefix__]').djangoSelect2({
            dropdownParent: modal  // https://stackoverflow.com/a/33884094
        })
        return false
    })

    // apply suggested job types on click
    $('.suggested-job-type').on('click', function (event) {
        let suggestion = $(this)
        $("#id_job_type").select2("trigger", "select", {
            data: { id: suggestion.data('id'), text: suggestion.text() }
        });
    })

    // conversion preview
    $('#id_job_type').on('change', function(event) {
        let content = $('#job_conversion_preview')
        content.empty()
        if (this.value === '') {
            // selected no type. nothing to compare
            return false
        }
        let url = content.data('url') + '?job_type_id=' + this.value
        $('#job_conversion_preview_loader').show()
        content.load(url, function (response, status, xhr) {
            $('#job_conversion_preview_loader').hide()
            if (status === 'error') {
                $(this).text(xhr.status + ' ' + xhr.statusText)
            }
        })
        return false
    })
});