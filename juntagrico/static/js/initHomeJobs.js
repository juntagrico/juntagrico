/*global define*/
define([], function () {
    
    var table = $("#filter-table").DataTable({
        "paging": false,
        "info": false,
        "ordering": false,
        "searching": false,
    });

    function format(place,starttime,endtime,area) {
      return '<div>Zeit: ' + starttime + '-' + endtime + '<br/>Ort: ' +place + '<br/>Bereich: ' +area + '</div>';
    }
    
    $('#filter-table').on('click', 'td.details-control', function () {
          var tr = $(this).closest('tr');
          var row = table.row(tr);

          if (row.child.isShown()) {
              // This row is already open - close it
              row.child.hide();
              tr.removeClass('shown');
          } else {
              // Open this row
              row.child(format(tr.data('place'),tr.data('starttime'),tr.data('endtime'),tr.data('area'))).show();
              tr.addClass('shown');
          }
      });
});