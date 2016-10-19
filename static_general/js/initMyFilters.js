define([], function () {

   $('#filter-table tfoot th').each( function () {
        var title = $(this).text();
        $(this).html( '<input type="text" placeholder="" style="width: 100%;" />' );
    } );

   var table = $('#filter-table').DataTable( {
        "paging":   false,
        "info":     false,
	"drawCallback": function( settings ) {
// do not like this but it works so far till i get around to find the correct api call
        	updateSendEmailButton($('#filter-table tr').size()-1);
    	}
    });

    function updateSendEmailButton(count) {
        if (count == 0) {
            $("button#send-email")
                .prop('disabled', true)
                .text("Email senden");
        } else if (count == 1) {
            $("button#send-email")
                .prop('disabled', false)
                .text("Email an diesen Loco senden");
        } else {
            $("button#send-email")
                .prop('disabled', false)
                .text("Email an diese " + count + " Locos senden");
        }
    }

    table.columns().every( function () {
        var that = this;
 
        $( 'input', this.footer() ).on( 'keyup change', function () {
            if ( that.search() !== this.value ) {
                that
                    .search( this.value )
                    .draw();
            }
        } );
    } );

    // Move the "Send email" button (and the corresponding form) to the same level as the filter input
    $("form#email-sender").appendTo("#filter_header div:first-child");

    $("form#email-sender").submit(function( event ) {
        var emails = [];
        $("#filter-table").find("tr").each(function () {
            var txt = $("td:eq(5)", this).text().trim();
            if (txt.length > 0)
                emails.push(txt);
        });
        $("#recipients").val(emails.join("\n"));
        $("#recipients_count").val(emails.length);
        $("#filter_value").val($("#filter-table_search").val());
        return;
    });

});
