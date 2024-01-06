$(function () {
    let additionalFile = function () {
        let $file = $(this);
        let $fileButton = $file.closest(".file-upload-button");
        let $fileUpload = $file.closest(".file-upload");

        // add a second one
        let $clone = $fileUpload.clone();
        $clone.find("button").text("Weitere Datei anhängen");
        $clone.find("input[type=file]").remove();
        $clone.find(".file-upload-button").append("<input type=\"file\">")
        $clone.find("input[type=file]").change(additionalFile).attr("name", "image-" + ($("input[type=file]").length + 1));
        $fileUpload.after($clone);

        // change the current to show the name instead of the button
        $fileButton.find("button").remove().end().find("input").hide();
        $fileButton.append($file.val().split('\\').pop() + ' ');
        let $removeButton = $("<a href='#'><i class='far fa-times-circle'></i></a>")
        $removeButton.on('click', removeFile)
        $fileButton.append($removeButton)
    };

    let removeFile = function () {
        $(this).closest(".file-upload").remove();
        return false
    }

    $("#attachements input[type=file]").change(additionalFile);
});