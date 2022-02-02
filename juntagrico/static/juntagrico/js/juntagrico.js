 function decorate_man_list_inputs() {
    $("#filter-table_filter label input").each(function () {
        $(this).addClass("form-control input-sm");
        $(this).css("width","auto");
        $(this).css("display","inline");
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

 function fetch_emails() {
    var emails = []
     $("#filter-table").find("tr").each(function () {
            var txt = $(".email", this).text().trim();
            if (txt.length > 0)
                for(var email of txt.split(",")){
                    emails.push(email.trim());
                }
        });
    return emails;
 }
 function email_submit() {
    $("form#email-sender").submit(function (event) {
        var emails = fetch_emails();

        $("#recipients").val(emails.join("\n"));
        $("#recipients_count").val(emails.length);
        return;
    });
}

function get_sb_config() {
    var sb_columns = true;
    if(typeof search_builder_enabled !== 'undefined' && search_builder_enabled){
        sb_columns = search_builder_columns;
    }
    return {
        columns: sb_columns
    };
}

function get_dom(){
    var dom_text = 'lfrtip';
    if(typeof search_builder_enabled !== 'undefined' && search_builder_enabled){
        dom_text = 'Q';
    }
    return dom_text;
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
            updateSendEmailButton(fetch_emails().length);
        },
        "language": {
            "search": search_field,
            searchBuilder: sb_lang
        },
        searchBuilder: get_sb_config(),
        dom : get_dom(),
    });
    return table;
}

function job_no_search_datatable() {
    $("#filter-table").DataTable({
        "responsive": true,
        "paging": false,
        "info": false,
        "ordering": false,
        "searching": false,
        "columnDefs": [
            {
                "targets": 'job-description',
                "visible": false
            },
            {
                "targets": ['job-date', 'job-status', 'job-name'],
                "responsivePriority": 1
            },
        ]
    });
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

function map_with_markers(locations, selected){
    let markers = []
    if(locations[0]) {
        $('#map-container').append('<div id="location-map">')
        let map = L.map('location-map').setView([locations[0].latitude, locations[0].longitude], 11);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        {attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'}).addTo(map);

        $.each(locations, function (i, location) {
            let marker = add_marker(location, map)
            if (location.name === selected) {
                marker.openPopup()
            }
            markers.push(marker)
        });
        let group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds(),{padding:[100,100]});
    }
    return markers
}

function add_marker(location, map){
    let marker = L.marker([location.latitude, location.longitude]).addTo(map);
    let description = "<strong>" + location.name + "</strong><br/>"
    if(location.addr_street) description += location.addr_street + "<br/>"
    if(location.addr_zipcode) description += location.addr_zipcode + " "
    if(location.addr_location) description += location.addr_location
    marker.bindPopup(description);
    marker.name = location.name
    return marker
}

function open_marker(markers, name){
    markers.forEach(function(marker) {
        if(name === marker.name){
            marker.openPopup()
        }
    })
}