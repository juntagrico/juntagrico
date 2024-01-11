/*global define*/
define([], function () {
    
    let table = $("#filter-table").DataTable();
    $("#email-sender").EmailButton(table)

    member_phone_toggle();
});