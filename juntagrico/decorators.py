from functools import wraps
from django.shortcuts import get_object_or_404
from juntagrico.models import Subscription
from django.http import HttpResponseRedirect


def primary_member_of_subscription(view):
    @wraps(view)
    def wrapper(request, subscription_id, *args, **kwargs):
        if request.user.is_authenticated():
            subscription = get_object_or_404(Subscription, id=subscription_id)
            if subscription.primary_member.id == request.user.member.id:
                return view(request, subscription_id=subscription_id, *args, **kwargs)
            else:
                return HttpResponseRedirect("/accounts/login/?next=" + str(request.get_full_path()))
        else:
            return HttpResponseRedirect("/accounts/login/?next=" + str(request.get_full_path()))

    return wrapper
