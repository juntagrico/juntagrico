from functools import wraps
from django.shortcuts import get_object_or_404
from juntagrico.models import Subscription
from django.http import HttpResponseRedirect


def primary_member_of_subscription(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            member = request.user.member
            subscription = get_object_or_404(
                Subscription, id=kwargs['subscription_id'])
            if subscription.primary_member.id == member.id:
                return view(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('/my/subscription/detail/')
        else:
            return HttpResponseRedirect('/accounts/login/?next=' + str(request.get_full_path()))

    return wrapper
