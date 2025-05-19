import datetime
from functools import wraps

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.utils.module_loading import import_string

from juntagrico.config import Config
from juntagrico.entity.jobs import AreaCoordinator
from juntagrico.entity.subs import SubscriptionPart
from juntagrico.models import Subscription
from juntagrico.util import temporal
from juntagrico.util.views_admin import date_from_get


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
                return redirect('subscription-landing')
        else:
            return redirect('login')

    return wrapper


def primary_member_of_subscription_of_part(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            member = request.user.member
            part = get_object_or_404(
                SubscriptionPart, id=kwargs.pop('part_id'))
            if part.subscription.primary_member.id == member.id:
                return view(request, *args, part=part, **kwargs)
            else:
                return redirect('subscription-landing')
        else:
            return redirect('login')
    return wrapper


def highlighted_menu(menu):
    def view_wrapper(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            request.active_menu = menu
            return view(request, *args, **kwargs)
        return wrapper
    return view_wrapper


def signup_session(view):
    """ wrapper for views that are part of the registration procedure
    the registration information is passed to the view as the second argument and changes to it are stored in the
    session automatically
    """
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        signup_manager = import_string(Config.signup_manager())(request)
        # make sure signup process is followed
        next_page = signup_manager.get_next_page()
        if next_page != request.resolver_match.url_name:
            return redirect(next_page)
        response = view(request, signup_manager, *args, **kwargs)
        return response
    return wrapper


def any_permission_required(*perms):
    """
    Decorator for views that checks whether a user has any of the given permissions
    """
    def check_perms(user):
        # check if the user has any of the permission
        if set(user.get_all_permissions()) & set(perms):
            return True
        return False
    return user_passes_test(check_perms)


def requires_permission_to_contact(func):
    def check_perms_to_contact(user):
        # check if user can contact members
        return (
            user.has_perm('juntagrico.is_area_admin') or
            user.has_perm('juntagrico.is_depot_admin') or
            user.has_perm('juntagrico.can_send_email') or
            AreaCoordinator.objects.filter(member=user.member, can_contact_member=True).exists()
        )
    return user_passes_test(check_perms_to_contact)(func)


def using_change_date(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        raw_date = request.session.get('changedate', None)
        date = None
        if raw_date:
            try:
                date = datetime.date.fromisoformat(raw_date)
            except ValueError:
                pass
        return view(request, date, *args, **kwargs)
    return wrapper


def date_range_view(view):
    """
    view_decorator:
    Sets the first two arguments, start and end, after request as follows:
    * arguments passed directly, e.g. from urls.py
    * GET variables `start_date` and `end_date`
    * Business year containing the GET variable `ref_date`, defaults to today
    """
    @wraps(view)
    def wrapper(request, start=None, end=None, *args, **kwargs):
        ref_date = date_from_get(request, 'ref_date')
        return view(
            request,
            start or date_from_get(request, 'start_date') or temporal.start_of_specific_business_year(ref_date),
            end or date_from_get(request, 'end_date') or temporal.end_of_specific_business_year(ref_date),
            *args, **kwargs
        )
    return wrapper
