$(function () {
    var additionalFile = function () {
        var $file = $(this);
        var $fileButton = $file.closest(".file-upload-button");
        var $fileUpload = $file.closest(".file-upload");
        var $attachements = $file.closest("#attachements");

        // add a second one
        var $clone = $fileUpload.clone();
        $clone.find("button").text("Weitere Datei anhängen");
        $clone.find("input[type=file]").remove();
        $clone.find(".file-upload-button").append("<input type=\"file\">")
        $clone.find("input[type=file]").change(additionalFile).attr("name", "image-" + ($("input[type=file]").length + 1));
        $fileUpload.after($clone);

        // change the current to show the name instead of the button
        $fileButton.find("button").remove().end().find("input").hide();
        $fileButton.append($file.val().split('\\').pop());
    };

    $("#attachements input[type=file]").change(additionalFile);
});