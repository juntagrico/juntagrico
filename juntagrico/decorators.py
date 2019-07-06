from functools import wraps

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect

from juntagrico.models import Subscription
from juntagrico.util.sessions import SessionObjectManager, CreateSubscriptionSessionObject


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


def create_subscription_session(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        som = SessionObjectManager(request, 'create_subscription', CreateSubscriptionSessionObject)
        session_object = som.data
        if request.user.is_authenticated:
            session_object.main_member = request.user.member
        if session_object.main_member is None and request.resolver_match.url_name is not 'signup':
            return redirect('signup')
        response = view(request, som.data, *args, **kwargs)
        som.store()
        return response

    return wrapper
