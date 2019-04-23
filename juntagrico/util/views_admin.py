from django.shortcuts import render


def subscription_management_list(management_list, renderdict, template, request):
    renderdict.update({
        'management_list': management_list,
    })
    return render(request, template, renderdict)
