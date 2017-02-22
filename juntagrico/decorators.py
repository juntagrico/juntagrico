from functools import wraps
from django.shortcuts import get_object_or_404
from juntagrico.models import Abo
from django.http import HttpResponseRedirect


def primary_loco_of_abo(view):
    @wraps(view)
    def wrapper(request, abo_id, *args, **kwargs):
        if request.user.is_authenticated():
            abo = get_object_or_404(Abo, id=abo_id)
            if abo.primary_loco.id == request.user.loco.id:
                return view(request, abo_id=abo_id, *args, **kwargs)
            else:
                return HttpResponseRedirect("/accounts/login/?next=" + str(request.get_full_path()))
        else:
            return HttpResponseRedirect("/accounts/login/?next=" + str(request.get_full_path()))

    return wrapper
