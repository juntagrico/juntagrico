/*global define*/
define([], function () {

    $("#filter-table thead th.table-search").each(function () {
        $(this).append("<input type='text' placeholder='' style='width: 100%;' class='form-control input-sm' />");
    });

    let free_slot_count = 'free-slot-count'
    let index = $('#filter-table th.'+free_slot_count).prevAll().length

    let table = $("#filter-table").DataTable({
        "responsive": true,
        "paging": false,
        "info": false,
        "ordering": false,
        "search": {
            "smart": true
        },
        "columnDefs": [
            {
                "targets": ['job-description', free_slot_count],
                "visible": false,
            },
            {
                "targets": ['job-date', 'job-status', 'job-name'],
                "responsivePriority": 1
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
        function( settings, data) {
            let min = parseInt( $('#free_slot_filter').val(), 10 );
            let free_slots = parseFloat( data[index] ) || 0;
            return isNaN(min) || free_slots >= min;
        }
    );

    $("#free_slot_filter").off("keyup change").on("keyup change", function () {
        table.draw();
    });
});
