/*global define, Dable */
define([], function () {
    var dable = new Dable("filter-table");

    dable.UpdateDisplayedRows();        // Update the table
    dable.UpdateStyle();                // Reapply our styles

    $("#emailSender").submit(function( event ) {
        var emails = [];
        $("#filter-table").find("tr").each(function () {
            var txt = $("td:eq(4)", this).text().trim();
            if (txt.length > 0)
                emails.push(txt);
        });
        $("#recipients").val(emails.join("\n"));
        $("#recipients_count").val(emails.length);
        $("#filter_value").val($("#filter-table_search").val());
        return;
    });

});
