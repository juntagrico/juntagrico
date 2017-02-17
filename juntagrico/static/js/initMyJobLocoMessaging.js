/*global define*/
define([], function () {

    $(".job-participant").click( function() {
        var firstName = $(this).text().trim().split(" ")[0],
            newGreeting = $("#locoMessageModal textarea").text().replace(/Hoi.*/, "Hoi " + firstName);
        $("#locoMessageModal textarea").text(newGreeting);
        $("#locoMessageModal .btn-message-send").text("Nachricht an " + firstName + " senden");
        $("#locoMessageModal").modal("show");
    });

    $("#locoMessageModal").on("shown.bs.modal", function () {
        $("#locoMessageModal textarea").focus();
    });

});