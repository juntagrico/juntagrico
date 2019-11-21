/*global define */
define([], function () {

    // preselect depot
    $("#depot").val(depot_id);
    
    map_with_markers(depots)

});