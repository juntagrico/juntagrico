/*global define*/
define([], function () {

    $("#filter-table thead th.table-search").each(function () {
        var title = $(this).text();
        $(this).append("<input type='text' placeholder='' style='width: 100%;' class='form-control input-sm' />");
    });

    var table = $("#filter-table").DataTable({
        "paging": false,
        "info": false,
        "ordering": false,
        "search": {
            "regex": true,
            "smart": false
        },
        "columnDefs": [
            {
                "targets": [ 5 ],
                "visible": false,
            },
        ],
        "language": {
            "search": "Suchen: "
        }
    });
    decorate_man_list_inputs();

    align_filter();

    table_column_search(table);

    // update on slot filter field
    $.fn.dataTable.ext.search.push(
        function( settings, data, dataIndex ) {
            var min = parseInt( $('#free_slot_filter').val(), 10 );
            var free_slots = parseFloat( data[5] ) || 0;
            if ( isNaN( min ) || free_slots >= min ) { return true; }
            return false;
        }
    );

    $("#free_slot_filter").off("keyup change").on("keyup change", function () {
        table.draw();
    });

    job_collapsible(table);

});