/*global define, Dable */
define([], function () {
    var dable = new Dable("filter-table");

    dable.UpdateDisplayedRows();        // Update the table
    dable.UpdateStyle();                // Reapply our styles

    var client = new ZeroClipboard(document.getElementById("copy-emails"), {
        moviePath: "/static/others/ZeroClipboard.swf"
    });

    client.on("load", function (client) {
        client.on("complete", function (client, args) {
            alert("Copied text to clipboard: " + args.text);
        });
    });
    setInterval(function () {
        var emails = [];
        $("#filter-table").find("tr").each(function () {
            var txt = $("td:eq(4)", this).text();
            if (txt)
                emails.push(txt);
        });
        client.setText(emails.join(", "));
    }, 200);
});