/*global define*/
define([], function () {

    $("#filter-table thead th.table-search").each(function () {
        var title = $(this).text();
        $(this).append("<input type='text' placeholder='' style='width: 100%;' class='form-control input-sm' />");
    });

    var table = $("#filter-table").DataTable({
        "responsive": true,
        "paging": false,
        "info": false,
        "ordering": false,
        "search": {
            "smart": true
        },
        "language": {
            "search": "Suchen: "
        },
        "columnDefs": [
            {
                "targets": [ 1 ],
                "visible": false
            }
        ]
    });
    decorate_man_list_inputs();

    align_filter();

    table_column_search(table);
});