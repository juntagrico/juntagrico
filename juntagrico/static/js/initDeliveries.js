/*global define*/
define([], function () {

	$('.collapse').on('shown.bs.collapse', function () {
	    $(this).parent().find(".fas").removeClass("fa-angle-right").addClass("fa-angle-down");
	});
	
	//The reverse of the above on hidden event:	
	$('.collapse').on('hidden.bs.collapse', function () {
	    $(this).parent().find(".fas").removeClass("fa-angle-down").addClass("fa-angle-right");
	});
});