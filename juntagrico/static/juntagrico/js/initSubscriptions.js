define([], function () {
    default_data_table();

    move_email_button();

    $("form#email-sender").submit(function (event) {
        var emails = [];
        $("#filter-table").find("tr").each(function () {
            var txt = $(".email", this).text().trim();
            if (txt.length > 0) {
                // Each Subscription might have a comma-separated list of email addresses
                multiple_emails = txt.split(",");
                for (var i = multiple_emails.length - 1; i >= 0; i--) {
                    emails.push(multiple_emails[i].trim());
                }
            }
        });
        var abo_count = $("#filter-table").find("tr").length - 1;
        var email_count = emails.length;
        $("#recipients").val(emails.join("\n"));
        $("#recipients_count").val(email_count);
        return;
    });
});
