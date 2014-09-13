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
                .text("Email an die Inhaber dieses Abo senden");
        } else {
            $("button#send-email")
                .prop('disabled', false)
                .text("Email an die Inhaber dieser " + dable.VisibleRowCount() + " Abos senden");
        }
    }

    // Move the "Send email" button (and the corresponding form) to the same level as the filter input
    $("form#email-sender").appendTo("#filter-table_header div:first-child");

    dable.UpdateDisplayedRows();        // Update the table
    dable.UpdateStyle();                // Reapply our styles

    $("form#email-sender").submit(function( event ) {
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
        var abo_count = $("#filter-table").find("tr").length - 1;
        var email_count = emails.length;
        $("#recipient_type_detail").val("Sie entsprechen die Haupt- und Mitinhaber von " +
            abo_count +
            " Abos.");
        $("#recipients").val(emails.join("\n"));
        $("#recipients_count").val(email_count);
        $("#filter_value").val($("#filter-table_search").val());
        return;
    });
});