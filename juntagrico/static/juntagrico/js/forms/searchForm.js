$(function () {
    let select_field = $('select[name="account"]')
    select_field.closest('.modal').on('shown.bs.modal', function (event) {
        let modal = $(this)
        modal.find('select').djangoSelect2({
            dropdownParent: modal
        }).select2('open')
    })
    select_field.on('change', function () {
        let input = $(this)
        let account = parseInt(input.val())
        if (!isNaN(account)) {
            input.closest('form').submit()
        }
    })
})
