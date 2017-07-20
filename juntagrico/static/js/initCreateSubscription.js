/*global define, $, mwember_shares, depots, destinations, google */
define(['modules/depotDistance'], function (depotDistance) {

    // check for the amount of shares of the member
    $("input[type=radio]").change(function () {
        var $checked = $(":checked");
        if ($checked.val() == "none") {
            $("#shares").val(1);
        } 
        else {
            $("#shares").val(Math.max(sizes[$checked.val()] - member_shares, 1));
        }
    }).change();

    $("input[type=radio]").change(function () {
        var $checked = $(":checked");
        if ($checked.val() == "none") {
            $("#start_date").hide(1000);
            $("#depot_container").hide(1000);
            $("#co_members").hide(1000);
            }
        else {
            $("#start_date").show(1000);
            $("#depot_container").show(1000);
            $("#co_members").show(1000);
        }
    }).change();
    
    $("#start_date").hide(1000);
    $("#depot_container").hide(1000);
    $("#co_members").hide(1000);
    $("input[type=radio]:checked").each(function () {
        var $checked = $(":checked");
        if ($checked.val() == "none") {
            $("#start_date").hide(1000);
            $("#depot_container").hide(1000);
            $("#co_members").hide(1000);
            }
        else {
            $("#start_date").show(1000);
            $("#depot_container").show(1000);
            $("#co_members").show(1000);
        }
    })


    // add additional member form
    $("#add-member").click(function () {
       	$(this).after($('<input type="hidden" id="add-member-value" name="add_member" value="true"/>'));
       	$(this).closest("form").off("submit").submit();
    });
    $("form").submit(function () {
        $("#add-member-value").remove();
    });

    // preselect depot
    if (window.depot_id) {
        $("#depot").val(window.depot_id);
    }

    depotDistance.calculate(member_addr, destinations, depots);

});
