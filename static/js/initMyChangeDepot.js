/*global define, $, loco_scheine, depots, destinations, google */
define(['modules/depotDistance'], function (depotDistance) {

    // preselect depot
    $("#depot").val(depot_id);

    depotDistance.calculate(loco_addr, destinations, depots);

});