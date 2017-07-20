$(function () {

    $("[type=checkbox].onoffswitch").each(function () {
        var name = $(this).attr('name');
        $(this).replaceWith('<div class="onoffswitch">'+
                            '<input type="checkbox" name="'+name+'" class="onoffswitch-checkbox" id="myonoffswitch'+name+'">'+
                            '<label class="bg-success onoffswitch-label" for="myonoffswitch'+name+'">'+
                            '<span class="onoffswitch-inner"></span>'+
                            '<span class="onoffswitch-switch"></span></label></div>');
    });

    $("[type=radio].onoffswitch").each(function () {
        var name = $(this).attr('name');
        var val = $(this).attr('value');
        $(this).replaceWith('<div class="onoffswitch">'+
                            '<input type="radio" name="'+name+'" value="'+val+'" class="onoffswitch-checkbox" id="myonoffswitch'+val+'">'+
                            '<label class="bg-success onoffswitch-label" for="myonoffswitch'+val+'">'+
                            '<span class="onoffswitch-inner"></span>'+
                            '<span class="onoffswitch-switch"></span></label></div>');
    });
});