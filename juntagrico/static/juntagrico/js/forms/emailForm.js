$(function () {
    // if all with active subcription are selected, selection of depots is obsolete
    $('[value="all_subscriptions"]').on('change', function () {
        $('#div_id_to_depots').toggle(!this.checked)
    })

    // update the number of recipients in the submit button
    $('#fieldset_to').on('change', function () {
        let submit_button = $('#submit-id-submit')
        const url = submit_button.data('countUrl')
        const data = $('#fieldset_to').serialize()
        $.ajax({
            type: url.length + data.length < 4000 ? 'GET' : 'POST',
            url: url,
            data: data,
            success: function (text) {
                $('#submit-id-submit').val(text)
            },
        });
    }).trigger('change')
})
