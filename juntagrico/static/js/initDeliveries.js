/*global define*/
define([], function () {

	$('.collapse').on('shown.bs.collapse', function () {
	    $(this).parent().find(".glyphicon").removeClass("glyphicon-chevron-right").addClass("glyphicon-chevron-down");
	});
	
	//The reverse of the above on hidden event:	
	$('.collapse').on('hidden.bs.collapse', function () {
	    $(this).parent().find(".glyphicon").removeClass("glyphicon-chevron-down").addClass("glyphicon-chevron-right");
	});
});