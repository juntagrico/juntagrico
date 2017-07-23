/*global define, $, loco_scheine, depots, destinations, google */
define(['modules/depotDistance'], function (depotDistance) {

    // preselect depot
    $("#depot").val(depot_id);

    depotDistance.calculate(member_addr, destinations, depots);

});