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
        "language": {
            "search": "Suchen: "
        }
    });
    decorate_man_list_inputs();

    align_filter();

    table_column_search(table);

    job_collapsible(table);

});