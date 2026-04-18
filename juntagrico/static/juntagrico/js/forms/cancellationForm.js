$(function () {
    // unset all activity areas
    $('#leave_all_areas').on('click', function () {
        $('[name="activity_areas"]').prop('checked', false)
        return false
    })

    $('input[type="number"]').inputSpinner();
    // update remaining share count
    let total_shares = parseInt($('#total_shares'))
    $('#id_shares').on('change', function () {
        let input = $(this)
        let to_be_canceled = parseInt(input.val()) || 0
        let remaining = parseInt(input.prop('max')) - to_be_canceled
        $('.remaining-shares').text(remaining)
        let iban_required = to_be_canceled > 0
        $('#id_iban').prop('required', iban_required)
        $('#div_id_iban .asteriskField').toggle(iban_required)
        $('.payback-details').toggle(iban_required)
    }).change()
})
