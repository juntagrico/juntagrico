from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from juntagrico.models import Subscription
from juntagrico.config import Config
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


def requires_main_member(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            main_member = request.user.member
        else:
            main_member = request.session.get('main_member')
        if main_member is None:
            return redirect('http://' + Config.server_url())
        return view(request, main_member, *args, **kwargs)

    return wrapper
