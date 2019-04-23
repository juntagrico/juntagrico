/*global define*/
define([], function () {
    
    var table = $("#filter-table").DataTable({
        "paging": false,
        "info": false,
        "ordering": false,
        "searching": false,
    });

    job_collapsible(table);
});