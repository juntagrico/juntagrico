$(function () {
    $("*[data-template-url]").click(function (event) {
        $.ajax({
            type: 'GET',
            url: $(this).data('templateUrl'),
            success: function (template_html) {
                tinymce.activeEditor.selection.setContent(template_html)
            },
            error: function (jqXHR, textStatus, errorThrown) {
                modal = $('#template_error')
                modal.find('.modal-title').text(textStatus)
                modal.find('.modal-body').text(errorThrown + ' - ' + jqXHR.responseText)
                modal.modal()
            }
        });
        event.preventDefault()
        return false
    });
})