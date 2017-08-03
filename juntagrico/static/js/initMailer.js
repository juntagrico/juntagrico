/*global define */
define([], function () {

    tinymce.init({
        selector: "textarea.mailer",
        'theme': "modern",
        'plugins': 'link',
        'relative_urls': false,
        "valid_styles": {
            '*': 'color,text-align,font-size,font-weight,font-style,text-decoration'
        },
        menu: {
            edit: {title: 'Edit', items: 'undo redo | cut copy paste | selectall'},
            insert: {title: 'Insert', items: 'link'},
            format: {title: 'Format', items: 'bold italic underline strikethrough superscript subscript | formats | removeformat'}
        }
    });
    $("#sendmail").click(function () {
        var editor = tinyMCE.get('message');
        editor.selection.select(editor.getBody(), true);
        $("#textMessage").val(editor.selection.getContent({format: 'text'}));
    });
    $("form").submit(function () {
        // If the textarea remains disabled, the content is not submitted in the request
        $("textarea#recipients").removeAttr("disabled");
        return;
    });
    $("#edit-recipients-action").on("click", function () {
        $("textarea#recipients").removeAttr("disabled");
        $(".recipients-info-detail").remove();
        $("#edit-recipients-action").remove();
    });
    $("#template").click(function () {
        $.ajax({
            type: 'GET',
            url: '/my/mailtemplate/' + $('#template-list').val() + '/',
            success: function (file_html) {
                tinyMCE.get('message').setContent(tinyMCE.get('message').getContent() + file_html);
            }
        });
    });

    $("#allsingleemail").change(function () {
        $("#singleemail").toggle();
        $('#allshares').prop('checked', false);
        $('#allsubscription').prop('checked', false);
        $('#all').prop('checked', false);
    });

    $("#allshares").change(function () {
        $('#allsingleemail').prop('checked', false);
        $("#singleemail").hide();
    });

    $("#all").change(function () {
        $('#allsingleemail').prop('checked', false);
        $("#singleemail").hide();
    });

    $("#allsubscription").change(function () {
        $('#allsingleemail').prop('checked', false);
        $("#singleemail").hide();
    });
});
