/*global define, $, loco_scheine, depots, destinations, google */
define(['modules/depotDistance'], function (depotDistance) {

    // check for the amount of shares of the loco
    $("input[type=radio]").change(function () {
        var $checked = $(":checked");
        if ($checked.val() === "small") {
            $("#scheine").val(Math.max(2 - loco_scheine, 0));
        } else if ($checked.val() === "big") {
            $("#scheine").val(Math.max(4 - loco_scheine, 0));
        } else if ($checked.val() === "house") {
            $("#scheine").val(Math.max(20 - loco_scheine, 0));
        }
        else {
            $("#scheine").val(1);
        }
    }).change();


    // add additional loco form
    $("#add-loco").click(function () {
        $(this).after($('<input type="hidden" id="add-loco-value" name="add_loco" value="true"/>'));
        $(this).closest("form").off("submit").submit();
    });
    $("form").submit(function () {
        $("#add-loco-value").remove();
    });

    // preselect depot
    $("#depot").val(depot_id);

    depotDistance.calculate(loco_addr, destinations, depots);

});