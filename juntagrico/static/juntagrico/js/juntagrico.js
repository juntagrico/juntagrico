$(function() {
    $.extend($.fn.dataTable.defaults, {
        "responsive": true,
        "paging": false,
        "info": false,
        "ordering": false,
        "search": {
            "smart": false,
            "regex": true
        },
        "searchBuilder": {
            "columns": ".search-builder-column"
        },
        "language": {
            "decimal": decimal_symbol[1],
            "search": search_field,
            "emptyTable": empty_table_string,
            "zeroRecords": zero_records_string,
            searchBuilder: sb_lang
        },
        "initComplete": function() {
            // activate column search inputs
            $("th.filter:not(:has(> input))", this).each(function () {
                $(this).append("<input type='text' placeholder='' class='form-control form-control-sm' />");
            });
            this.api().columns().every(function () {
                let that = this;
                $("input", this.header()).on("keyup change", function () {
                    if (that.search() !== this.value) {
                        that.search(this.value, true, false).draw();
                    }
                }).on("click", function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                });
            });
        }
    });
});

$.fn.EmailButton = function(tables, selector='.email') {
    tables = Array.isArray(tables)?tables:[tables]
    let form = $(this)

    let fetch_emails = function() {
        let table_nodes = tables.map((table) => table.table().node())
        let table_emails = $(selector, table_nodes).text().trim().replace(/[\s,]+/gm, ',');
        if (table_emails !== "")
            return new Set(table_emails.split(','))
        return new Set()
    }

    // Move the button (and the corresponding form) to the same level as the filter input
    form.appendTo("#filter-table_wrapper .row:first-child > div:first-child")
    // On submit collect emails from table and first.
    form.submit(function (event) {
        let emails = fetch_emails()
        $("[name='recipients']", this).val(Array.from(emails).join("\n"))
        $("[name='recipients_count']", this).val(emails.size)
    })

    // update counter in email button when table if filtered
    for (let table of tables) {
        table.on('draw', function() {
            const count = fetch_emails().size
            let button = $("[type='submit']", form)
            button.prop("disabled", count === 0)
            button.text(email_button_string[Math.min(2, count)].replace("{count}", count))
        }).draw()
    }
    return this;
};

function member_phone_toggle() {
    let show_co_members = $("#show_co_members")
    let show_phone_numbers = $("#show_phone_numbers")
    // initialize correct value after reload
    $('.co-member').toggle(show_co_members.is(':checked'));
    $('.phone-number').toggle(show_phone_numbers.is(':checked'));
    // change on click
    show_co_members.change(function () {
        $('.co-member').toggle(this.checked);
    });
    show_phone_numbers.change(function () {
        $('.phone-number').toggle(this.checked);
    });
}

function area_slider() {
    $("input.switch").change(function () {
        if ($(this).is(':checked')) {
            $.get("/my/area/" + $(this).attr('value') + "/join");
        } else {
            $.get("/my/area/" + $(this).attr('value') + "/leave");
        }

    })
}

function map_with_markers(locations, selected) {
    let markers = []
    if (locations[0]) {
        $('#map-container').append('<div id="location-map">')
        let map = L.map('location-map').setView([locations[0].latitude, locations[0].longitude], 11);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            {
                attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                    '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'
            }).addTo(map);

        $.each(locations, function (i, location) {
            let marker = add_marker(location, map)
            if (location.name === selected) {
                marker.openPopup()
            }
            markers.push(marker)
        });
        let group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds(), {padding: [100, 100]});
    }
    return markers
}

function add_marker(location, map) {
    let marker = L.marker([location.latitude, location.longitude]).addTo(map);
    let description = "<strong>" + location.name + "</strong><br/>"
    if (location.addr_street) description += location.addr_street + "<br/>"
    if (location.addr_zipcode) description += location.addr_zipcode + " "
    if (location.addr_location) description += location.addr_location
    marker.bindPopup(description);
    marker.name = location.name
    return marker
}

function open_marker(markers, name) {
    markers.forEach(function (marker) {
        if (name === marker.name) {
            marker.openPopup()
        }
    })
}
