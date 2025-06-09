$(function () {
    $(".file-upload-button").on('click', function (event) {
        $(this).prev().trigger('click')
        event.preventDefault
        return false
    })

    $('#id_attachments0').on('change', function () {
        let $this = $(this)

        // add new uploader below with updated id and name
        let file_upload = $this.closest('.file-upload')
        let new_file_upload = file_upload.clone(true)
        let count = $('.file-upload').length
        new_file_upload.find('input').attr('id', 'id_attachments' + count).attr("name", "attachments" + count).val('');
        file_upload.prevAll('label').attr('for', 'id_attachments' + count)
        file_upload.after(new_file_upload)

        // show filename and button to remove on current
        $this.next().remove()
        let remove_button = $('<a href="#"><i class="far fa-times-circle text-dark"></i></a>')
        remove_button.on('click', removeFile)
        $this.after(remove_button).after('<span class="mr-2 mb-2">' + $this.val().split('\\').pop() + '</span>')
    });

    function removeFile() {
        $(this).closest('.file-upload').remove();
        // renumber the file inputs
        $('.file-upload').each(function (i) {
            $(this).find('input').attr('id', 'id_attachments' + i).attr("name", "attachments" + i);
        })
        let current = $('.file-upload:last-child')
        current.prevAll('label').attr('for', current.find('input').attr('id'))
        return false
    }
});