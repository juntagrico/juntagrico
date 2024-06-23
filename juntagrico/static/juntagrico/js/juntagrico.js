// Datatables
$(function () {
    if ($.fn.dataTable) {
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
            "initComplete": function (settings) {
                let api = new $.fn.dataTable.Api(settings)
                // activate column search inputs
                if (api.init().searching !== false) {
                    $("th.filter:not(:has(> input))", this).each(function () {
                        $(this).append("<input type='text' placeholder='' class='form-control form-control-sm' />");
                    });
                }
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
    }
});

function email_button(action, csrf_token) {
    function get_emails(dt) {
        return fetch_unique_from_table(get_selected_or_all(dt), '.email')
    }
    return {
        text: email_button_string[0],
        init: function (dt, node, config) {
            let that = this;
            dt.on('draw select.dt.DT deselect.dt.DT', function () {
                const count = get_emails(dt).size
                that.enable(count > 0)
                that.text(email_button_string[Math.min(2, count)].replace("{count}", count))
            })
        },
        action: function (e, dt, node, config) {
            let emails = get_emails(dt)
            post(action, csrf_token, {
                recipients: Array.from(emails).join("\n"),
                recipients_count: emails.size,
            })
        }
    }
}

function share_id_button(text, action, csrf_token, selector, confirm=null) {
    return {
        text: text,
        init: function (dt, node, config) {
            let that = this;
            dt.on('draw select.dt.DT deselect.dt.DT', function () {
                that.enable(get_selected_or_all(dt).to$().find(selector).length > 0)
            })
            that.disable()
        },
        action: function (e, dt, node, config) {
            let shares = fetch_unique_from_table(get_selected_or_all(dt), selector)
            if (confirm) {
                let confirm_text = confirm[Math.min(2, shares.size)-1].replace('{count}', shares.size)
                if (!window.confirm(confirm_text)) return
            }
            post(action, csrf_token, {
                share_ids: Array.from(shares).join("_"),
            })
        }
    }
}


function fetch_unique_from_table(node, selector) {
    // TODO make more robust for case, where there is no space around the node texts.
    let entries = $(selector, node).text().trim().replace(/[\s,]+/gm, ',');
    if (entries !== "")
        return new Set(entries.split(','))
    return new Set()
}

function get_selected_or_all(dt) {
    let selected = dt.rows({selected: true, search: 'applied'})
    return selected.any() ? selected.nodes() : dt.rows({search: 'applied'}).nodes()
}

function post(action, csrf_token, data) {
    let form = $('<form action="' + action + '" method="POST">' + csrf_token + '</form>')
    for (const key in data) {
        form.append($('<input type="hidden" name="' + key + '" value="' + data[key] + '"/>'))
    }
    $('body').append(form)
    form.submit()
}


$.fn.EmailButton = function (tables, selector = '.email') {
    tables = Array.isArray(tables) ? tables : [tables]
    let form = $(this)

    let fetch_emails = function () {
        let table_nodes = tables.map((table) => table.table().node())
        let table_emails = $(selector, table_nodes).text().trim().replace(/[\s,]+/gm, ',');
        if (table_emails !== "")
            return new Set(table_emails.split(','))
        return new Set()
    }

    // Move the button (and the corresponding form) to the same level as the filter input
    if (tables.length === 1)
        form.appendTo($(".row:first-child > div:first-child", $(tables[0].table().node()).parent().parent().parent()))
    // On submit collect emails from table and first.
    form.submit(function (event) {
        let emails = fetch_emails()
        $("[name='recipients']", this).val(Array.from(emails).join("\n"))
        $("[name='recipients_count']", this).val(emails.size)
    })

    // update counter in email button when table if filtered
    for (let table of tables) {
        table.on('draw', function () {
            const count = fetch_emails().size
            let button = $("[type='submit']", form)
            button.prop("disabled", count === 0)
            button.text(email_button_string[Math.min(2, count)].replace("{count}", count))
        }).draw()
    }
    return this;
};


// Form Elements

$.fn.ToggleButton = function (selector) {
    let button = $(this)
    // initialize correct value after reload
    $(selector).toggle(button.is(':checked'));
    // change on click
    button.change(function () {
        $(selector).toggle(this.checked);
    });
}

$.fn.AjaxSlider = function (activate_url, disable_url, placeholder = '{value}') {
    $(this).change(function () {
        let slider = $(this)
        if (slider.is(':checked')) {
            $.get(activate_url.replace(placeholder, slider.val()));
        } else {
            $.get(disable_url.replace(placeholder, slider.val()));
        }
    })
}


// Maps

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
