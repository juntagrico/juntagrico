import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, render, redirect

from juntagrico.entity.subs import Subscription
from juntagrico.entity.subtypes import SubscriptionType, SubscriptionProduct
from juntagrico.forms import SubscriptionPartOrderForm
from juntagrico.util.management import create_subscription_parts
from juntagrico.view_decorators import primary_member_of_subscription


@login_required
def landing(request):
    """
    Forward to overview or detail view depending on subscription situation
    """
    member = request.user.member
    relevant_subs = member.subscriptionmembership_set.exclude(leave_date__lte=datetime.date.today())
    count = relevant_subs.count()
    if count == 0:
        return none(request)
    elif count == 1:
        return redirect('subscription-single', subscription_id=relevant_subs.first().subscription.id)

    # else: show selection of subscriptions
    return render(request, 'juntagrico/my/subscription/landing.html', {
        'member': member,
        'subscription_memberships': relevant_subs.order_by(F('join_date').asc(nulls_last=True)),
    })


@login_required
def none(request):
    """
    Page, if member has no subscription
    """
    return render(request, 'juntagrico/my/subscription/none.html', {
        'member': request.user.member,
    })


@login_required
def single(request, subscription_id=None):
    """
    Detail view of a subscription of a member
    """
    member = request.user.member

    if subscription_id is None:
        subscription = member.subscription_current
    else:
        subscription = Subscription.objects.filter(id=subscription_id, subscriptionmembership__member=member).first()

    if not subscription:
        return redirect('subscription-landing')

    # count assignments of subscription
    subscription = Subscription.objects.annotate_assignment_counts(
        of_member=member,
        prefix='member_'
    ).annotate_assignments_progress().get(pk=subscription)

    subscription_membership = member.subscriptionmembership_set.get(subscription=subscription)
    return render(request, 'juntagrico/my/subscription/single.html', {
        'member': member,
        'subscription': subscription,
        'subscription_membership': subscription_membership,
        'can_change_part': SubscriptionType.objects.normal().visible().count() > 1,
        'has_extra': SubscriptionType.objects.is_extra().visible().exists()
    })


@primary_member_of_subscription
def part_order(request, subscription_id, extra=False):
    """
    Order parts on a subscription
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    products = SubscriptionProduct.objects.filter(is_extra=extra).all
    if request.method == 'POST':
        form = SubscriptionPartOrderForm(subscription, request.POST, product_method=products)
        if form.is_valid():
            create_subscription_parts(subscription, form.get_selected(), True)
            return redirect('subscription-single', subscription_id=subscription_id)
    else:
        form = SubscriptionPartOrderForm(product_method=products)
    return render(request, 'juntagrico/my/subscription/part/order.html', {
        'extra': extra,
        'form': form,
        'selected_depot': subscription.depot,
    })
