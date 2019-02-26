define([], function () {
    $("#filter-table thead th").each(function () {
        var title = $(this).text();
        $(this).append("<input type='text' placeholder='' style='width: 100%;' class='form-control input-sm' />");
    });

    var table = $("#filter-table").DataTable({
        "paging": false,
        "info": false,
        "search": {
            "regex": true,
            "smart": false
        },
        "drawCallback": function (settings) {
            // do not like this but it works so far till i get around to find the correct api call
            updateSendEmailButton($("#filter-table tr").length - 2);
        },
        "language": {
            "search": "Suchen: "
        }
    });

    $("#filter-table_filter label input").each(function () {
        $(this).addClass("form-control input-sm");
        $(this).css("width","auto");
        $(this).css("display","inline");
    });

    $("#filter-table_filter").each(function () {
        $(this).css("text-align","right");
    });

    function updateSendEmailButton(count) {
        if (count == 0) {
            $("button#send-email")
                .prop("disabled", true)
                .text(email_string);
        } else if (count == 1) {
            $("button#send-email")
                .prop("disabled", false)
                .text(email_single_string+" "+member_string+" "+send_string);
        } else {
            $("button#send-email")
                .prop("disabled", false)
                .text( email_multi_string+" " + count + " "+members_string+" "+send_string);
        }
    }

    table.columns().every(function () {
        var that = this;
        $("input", this.header()).on("keyup change", function () {
            if (that.search() !== this.value) {
                that.search(this.value,true,false).draw();
            }
        });
        $("input", this.header()).on("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    // Move the "Send email" button (and the corresponding form) to the same level as the filter input
    $("form#email-sender").appendTo("#filter-table_header div:first-child");


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
