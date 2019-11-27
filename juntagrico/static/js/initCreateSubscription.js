/*global define, $, mwember_shares, depots, destinations, google */
define([], function () {

    if (typeof depots !== 'undefined') {
        // preselect depot
        if (window.depot_id) {
            $("#depot").val(window.depot_id);
        }
        map_with_markers(depots)
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
