$(function ($) {
    let description = $('#id_type_description')
    let duration = $('#id_type_duration')
    $('#id_type').on('change', function () {
        if (this.value !== '') {
            description.load(description.data('url').replace('99', this.value))
            duration.load(duration.data('url').replace('99', this.value))
        }
    })
})
