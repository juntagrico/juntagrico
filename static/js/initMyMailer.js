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
    $("button.btn-success").click(function () {
        var editor = tinyMCE.get('message');
        editor.selection.select(editor.getBody(), true);
        $("#textMessage").val(editor.selection.getContent({format: 'text'}));
    });
    $("form").submit(function () {
        // If the textarea remains disabled, the content is not submitted in the request
        $("textarea#recipients").removeAttr("disabled");
        return;
    });
});