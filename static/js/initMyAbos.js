/*global define, Dable */
define([], function () {
    var dable = new Dable("filter-table");

    dable.UpdateDisplayedRows();        // Update the table
    dable.UpdateStyle();                // Reapply our styles

    $("#emailSender").submit(function( event ) {
        var emails = [];
        $("#filter-table").find("tr").each(function () {
            var txt = $("td:eq(5)", this).text().trim();
            if (txt.length > 0) {
                // Each Abo might have a comma-separated list of email addresses
                multiple_emails = txt.split(",");
                for (var i = multiple_emails.length - 1; i >= 0; i--) {
                    emails.push(multiple_emails[i].trim());
                }
            }
        });
        $("#recipients").val(emails.join("\n"));
        $("#recipients_count").val(emails.length);
        $("#filter_value").val($("#filter-table_search").val());
        return;
    });
});