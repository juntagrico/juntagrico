 function decorate_man_list_inputs() {
    $("#filter-table_filter label input").each(function () {
        $(this).addClass("form-control input-sm");
        $(this).css("width","auto");
        $(this).css("display","inline");
    });
 }

 function job_collapsible(table, format=default_job_format) {
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
 }

 function table_column_search(table) {
    table.columns().every(function () {
        var that = this;
        $("input", this.header()).on("keyup change", function () {
            if (that.search() !== this.value) {
                that.search(this.value,true,false).draw();
            }
        });
        $("input", this.header()).on("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
        });
    });
 }

 function align_filter() {
     $("#filter-table_filter").each(function () {
        $(this).css("text-align","right");
    });
 }

 function updateSendEmailButton(count) {
        if (count == 0) {
            $("button#send-email")
                .prop("disabled", true)
                .text(email_string);
        } else if (count == 1) {
            $("button#send-email")
                .prop("disabled", false)
                .text(email_single_string+" "+member_string+" "+send_string);
        } else {
            $("button#send-email")
                .prop("disabled", false)
                .text( email_multi_string+" " + count + " "+members_string+" "+send_string);
        }
}

function move_email_button() {
    // Move the "Send email" button (and the corresponding form) to the same level as the filter input
    $("form#email-sender").appendTo("#filter_header div:first-child");
}

function email_submit() {
    $("form#email-sender").submit(function (event) {
        var emails = [];
        $("#filter-table").find("tr").each(function () {
            var txt = $(".email", this).text().trim();
            if (txt.length > 0)
                emails.push(txt);
        });
        $("#recipients").val(emails.join("\n"));
        $("#recipients_count").val(emails.length);
        return;
    });
}

function default_data_table() {
    var table = $("#filter-table").DataTable({
        "paging": false,
        "info": false,
        "search": {
            "regex": true,
            "smart": false
        },
        "drawCallback": function (settings) {
            // do not like this but it works so far till i get around to find the correct api call
            updateSendEmailButton($("#filter-table tbody tr").length);
        },
        "language": {
            "search": "Suchen: "
        }
    });
    return table;
}

function default_job_format(place,starttime,endtime,area) {
      return '<div>Zeit: ' + starttime + '-' + endtime + '<br/>Ort: ' +place + '<br/>Bereich: ' +area + '</div>';
}

function area_slider() {
    $("input.switch").change(function () {
        if($(this).is(':checked')){
            $.get( "/my/area/"+$(this).attr('value')+"/join");
        }
        else {
            $.get( "/my/area/"+$(this).attr('value')+"/leave");
        }

    })
}

function map_with_markers(depots){
    markers = []
    if(depots[0]) {
        var map = L.map('depot-map').setView([depots[0].latitude, depots[0].longitude], 11);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        {attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'}).addTo(map);

        $.each(depots, function (i, depot) {
            var marker = add_marker(depot, map)
            markers.push(marker)
        });
        var group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds(),{padding:[100,100]});
    }
    return markers
}

function add_marker(depot, map){
    var marker = L.marker([depot.latitude, depot.longitude]).addTo(map);
    marker.bindPopup("<b>" + depot.name + "</b><br/>" +
            depot.addr_street + "<br/>"
            + depot.addr_zipcode + " " + depot.addr_location);
    return marker
}
