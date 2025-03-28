/*global define, $, mwember_shares, depots, destinations, google */
define([], function () {
    let depot_element = document.getElementById('depots')
    if (depot_element) {
        let depots = JSON.parse(depot_element.textContent)
        let selected_depot_element = document.getElementById('selected_depot')
        let selected_depot = null
        if (selected_depot_element) {
            selected_depot = JSON.parse(selected_depot_element.textContent)
        }
        let [map, markers] = map_with_markers(depots, selected_depot)
        init_depot_map(map, markers)
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
    if($().inputSpinner) {
        $("input[type='number']").inputSpinner();
    }
});
