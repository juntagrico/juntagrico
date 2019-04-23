/*global define*/
define([], function () {

	$('.collapse').on('shown.bs.collapse', function () {
	    $(this).parent().prev().addClass("shown");
	});
	
	//The reverse of the above on hidden event:	
	$('.collapse').on('hidden.bs.collapse', function () {
	    $(this).parent().prev().removeClass("shown");
	});
});