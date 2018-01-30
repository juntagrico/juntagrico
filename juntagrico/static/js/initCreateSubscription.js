/*global define, $, mwember_shares, depots, destinations, google */
define(['modules/depotDistance'], function (depotDistance) {

    // preselect depot
    if (window.depot_id) {
        $("#depot").val(window.depot_id);
    }

    depotDistance.calculate(member_addr, destinations, depots);

});
