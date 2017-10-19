$(function () {

    $("[type=checkbox].onoffswitch").each(function () {
        var name = $(this).attr('name');
        var checked = $(this).attr('checked');
        var val = $(this).attr('value');
        var id = $(this).attr('id');
        if(!id)
            id="myonoffswitch"+name;
        var valstring = ''
        if(val!==undefined)
            valstring= 'value="'+val+'"'
        var checked_string =''
        if(checked)
            checked_string='checked="checked"';
        $(this).replaceWith('<div class="onoffswitch">'+
                            '<input type="checkbox" name="'+name+'" '+valstring+' '+ checked_string +' class="onoffswitch-checkbox" id="'+id+'">'+
                            '<label class="bg-success onoffswitch-label" for="'+id+'">'+
                            '<span class="onoffswitch-inner"></span>'+
                            '<span class="onoffswitch-switch"></span></label></div>');
    });

    $("[type=radio].onoffswitch").each(function () {
        var name = $(this).attr('name');
        var val = $(this).attr('value');
        var checked = $(this).attr('checked');
        var checked_string =''
        if(checked)
            checked_string='checked="checked"';
        $(this).replaceWith('<div class="onoffswitch">'+
                            '<input type="radio" name="'+name+'" value="'+val+'" '+ checked_string +' class="onoffswitch-checkbox" id="myonoffswitch'+val+'">'+
                            '<label class="bg-success onoffswitch-label" for="myonoffswitch'+val+'">'+
                            '<span class="onoffswitch-inner"></span>'+
                            '<span class="onoffswitch-switch"></span></label></div>');
    });
});