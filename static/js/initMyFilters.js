/*global define, Dable */
define([], function () {
    var dable = new Dable("filter-table");

    var OriginalUpdateDisplayedRows = dable.UpdateDisplayedRows;
    dable.UpdateDisplayedRows = function (body) {
        OriginalUpdateDisplayedRows(body);
        updateSendEmailButton(dable.VisibleRowCount());
    };

    function updateSendEmailButton(count) {
        if (count == 0) {
            $("button#send-email")
                .prop('disabled', true)
                .text("Email senden");
        } else if (count == 1) {
            $("button#send-email")
                .prop('disabled', false)
                .text("Email an diesem Loco senden");
        } else {
            $("button#send-email")
                .prop('disabled', false)
                .text("Email an diese " + dable.VisibleRowCount() + " Locos senden");
        }
    }

    dable.UpdateDisplayedRows();        // Update the table
    dable.UpdateStyle();                // Reapply our styles

    $("form#email-sender").submit(function( event ) {
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
