/*global define, $, mwember_shares, depots, destinations, google */
define([], function () {

    if (typeof depots !== 'undefined') {
        // preselect depot
        if (window.depot_id) {
            $("#depot").val(window.depot_id);
        }
        var map = L.map('depot-map').setView([depots[0].latitude, depots[0].longitude], 11);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        {attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'}).addTo(map);

        markers = []
        $.each(depots, function (i, depot) {
                    var marker = L.marker([depot.latitude, depot.longitude]).addTo(map);
                    marker.bindPopup("<b>" + depot.name + "</b><br/>" +
                            depot.addr_street + "<br/>"
                            + depot.addr_zipcode + " " + depot.addr_location);
                    markers.push(marker)
        });
        var group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds(),{padding:[100,100]});

    }

    function total_selected_subs() {
        var amount = 0
        $("input[type='number'][name^='amount']").each(function(){
            amount += parseInt(this.value)
        })
        return amount
    }

    // interactive checkbox
    $("input[name='subscription'][value='-1']").change(function(){
        if (this.checked) {
            $("input[type='number'][name^='amount']+div input").val(0).change()
        } else if (total_selected_subs() == 0)  {
            this.checked = true
        }
    })
    $("input[type='number'][name^='amount']").change(function(){
        $("input[name='subscription'][value='-1']").prop('checked', total_selected_subs() == 0)
    })

    // show Spinner in multi selection
    $("input[type='number']").inputSpinner();
});
