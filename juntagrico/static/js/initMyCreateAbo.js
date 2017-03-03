/*global define, $, loco_scheine, depots, destinations, google */
define(['modules/depotDistance'], function (depotDistance) {

    // check for the amount of shares of the loco
    $("input[type=radio]").change(function () {
        var $checked = $(":checked");
        if ($checked.val() === "none") {
            $("#scheine").val(1);
        } 
        else {
            $("#scheine").val(Math.max(sizes[$checked.val()] - loco_scheine, 0));
        }
    }).change();


    // check for the amount of shares of the loco
    $("input[type=radio]").change(function () {
        var $checked = $(":checked");
        if ($checked.val() === "none") {
            $("#start_date").hide();
}
        else {
            $("#start_date").show();
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
    if (window.depot_id) {
        $("#depot").val(window.depot_id);
    }

    depotDistance.calculate(loco_addr, destinations, depots);

});
