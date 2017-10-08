/*global define*/
define([], function () {

    $("#filter-table thead th").each(function () {
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
    
    function format(subscription_size, text) {
    	return '<div>Abogrösse: ' + subscription_size + '</br>Gemüsetabelle: ' + text + '</div>';
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
              row.child(format(tr.data('subscription_size'), tr.data('text'))).show();
              tr.addClass('shown');
          }
      });
});