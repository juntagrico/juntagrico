$(function () {
    // if all with active subcription are selected, selection of depots is obsolete
    $('#id_to_list_1').on('change', function () {
        $('#div_id_to_depots').toggle(!this.checked)
    })

    // update the number of recipients in the submit button
    $('#fieldset_to').on('change', function () {
        let submit_button = $('#submit-id-submit')
        $.ajax({
            type: 'GET',
            url: submit_button.data('countUrl'),
            data: $('#fieldset_to').serialize(),
            success: function (text) {
                $('#submit-id-submit').val(text)
            },
        });
    }).trigger('change')
})
