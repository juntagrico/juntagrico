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
            updateSendEmailButton($("#filter-table tr").size() - 2);
        },
        "language": {
            "search": "Suchen: "
        }
    });

    function updateSendEmailButton(count) {
        if (count == 0) {
            $("button#send-email")
                .prop("disabled", true)
                .text("Email senden");
        } else if (count == 1) {
            $("button#send-email")
                .prop("disabled", false)
                .text("Email an diesen "+member_string+" senden");
        } else {
            $("button#send-email")
                .prop("disabled", false)
                .text("Email an diese " + count + " "+members_string+" senden");
        }
    }

    table.columns().every(function () {
        var that = this;
        $("input", this.header()).on("keyup change", function () {
            if (that.search() !== this.value) {
                that.search(this.value).draw();
            }
        });
        $("input", this.header()).on("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    // Move the "Send email" button (and the corresponding form) to the same level as the filter input
    $("form#email-sender").appendTo("#filter_header div:first-child");

    $("form#email-sender").submit(function (event) {
        var emails = [];
        $("#filter-table").find("tr").each(function () {
            var txt = $("td:eq(5)", this).text().trim();
            if (txt.length > 0)
                emails.push(txt);
        });
        $("#recipients").val(emails.join("\n"));
        $("#recipients_count").val(emails.length);
        return;
    });

});
