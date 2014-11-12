/*global define*/
define([], function () {

    $(".job-participant").click( function() {
        var vorname = $(this).text().trim().split(" ")[0];
        $("#locoMessageModal textarea").prepend("Hoi " + vorname + "\n\n");
        $("#locoMessageModal .btn-message-send").text("Nachricht an " + $(this).text() + " senden");
        $("#locoMessageModal").modal("show");
    });

    $("#locoMessageModal").on("shown.bs.modal", function () {
        $("#locoMessageModal textarea").focus();
    });

});