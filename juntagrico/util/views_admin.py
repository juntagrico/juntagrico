from django.shortcuts import render

def subscription_management_list(list, renderdict, template, request):
    renderdict.update({
        'management_list': list,
    })
    return render(request, template, renderdict)
    
