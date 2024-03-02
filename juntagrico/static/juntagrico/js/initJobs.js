/*global define*/
define([], function () {
    let table = $("#filter-table").DataTable();

    // update on slot filter field
    let index = $('#filter-table th.free-slot-count').prevAll().length
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
