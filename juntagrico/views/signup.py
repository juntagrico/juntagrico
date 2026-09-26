from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from juntagrico.config import Config
from juntagrico.entity.member import Invitee
from juntagrico.forms.account import AccountInvitationForm
from juntagrico.forms.membership import MembershipInvitationForm
from juntagrico.mailer import membernotification
from juntagrico.views.share import ShareInvitationForm


def invitation_invalid(request, template_name='juntagrico/signup/invitation/invalid.html'):
    return render(request, template_name)


def invitation(request, key, template_name='juntagrico/signup/invitation/landing.html'):
    invitee = Invitee.objects.filter(key=key).first()
    if invitee is None:
        return invitation_invalid(request)
    return render(request, template_name, {'key': key, 'invitee': invitee})


def invitation_to_new(request, key, template_name='juntagrico/signup/invitation/new.html'):
    logout(request)
    invitee = Invitee.objects.filter(key=key).first()
    if invitee is None:
        return invitation_invalid(request)

    subscription = invitee.subscription

    if request.method == 'POST':
        account_form = AccountInvitationForm(request.POST)
    else:
        account_form = AccountInvitationForm(initial={
            'first_name': invitee.first_name,
            'last_name': invitee.last_name,
            'email': invitee.email,
        })
    
    if Config.enable_membership():
        if request.method == 'POST':
            membership_form = MembershipInvitationForm(request.POST)
        else:
            membership_form = MembershipInvitationForm()
    else:
        membership_form = None

    if Config.enable_shares():
        # count share underflow, assuming all other invitees order as suggested
        required_shares = invitee.required_shares()
        if request.method == 'POST':
            share_form = ShareInvitationForm(required_shares, data=request.POST)
        else:
            share_form = ShareInvitationForm(
                required_shares, initial={'of_member': invitee.shares}
            )
    else:
        share_form = None

    if request.method == 'POST':
        valid = account_form.is_valid()
        if valid and membership_form:
            valid = membership_form.is_valid()
        if valid and share_form:
            valid = share_form.is_valid()
        if valid:
            member = account_form.save()
            password = member.set_password()
            member.join_subscription(subscription)
            share_count = 0
            if share_form:
                share_count = share_form.save(member)
            if membership_form:
                membership_form.save(member, member.signup_comment)
            invitee.delete()
            membernotification.welcome_co_member(
                member,
                password,
                share_count
            )
            return redirect('welcome')

    return render(
        request,
        template_name,
        {
            'invitee': invitee,
            'subscription': subscription,
            'account_form': account_form,
            'membership_form': membership_form,
            'membership_fee': Config.membership('fee'),
            'share_form': share_form,
            'required_shares_for_membership': Config.membership('required_shares') if share_form else 0,
        },
    )


@login_required
def invitation_to_existing(request, key, template_name='juntagrico/signup/invitation/existing.html'):
    invitee = Invitee.objects.filter(key=key).first()
    if invitee is None:
        return invitation_invalid(request)

    account = request.user.member
    # TODO: handle case, where account already has a subscription

    # if account has fewer shares than needed, show share order form
    share_form = None
    if Config.enable_shares():
        existing_shares = account.usable_shares.count()
        required_shares = invitee.required_shares()
        if required_shares > existing_shares:
            required = {
                'total': required_shares, 'for_primary': required_shares - existing_shares
            }
            if request.method == 'POST':
                share_form = ShareInvitationForm(required, existing_shares, data=request.POST)
            else:
                share_form = ShareInvitationForm(required, existing_shares)

    membership_form = None
    if Config.enable_membership():
        if share_form and not account.memberships.not_canceled().exists():
            if request.method == 'POST':
                membership_form = MembershipInvitationForm(request.POST)
            else:
                membership_form = MembershipInvitationForm()

    if request.method == 'POST':
        valid = True
        if membership_form:
            valid = membership_form.is_valid()
        if valid and share_form:
            valid = share_form.is_valid()
        if valid:
            account.join_subscription(invitee.subscription)
            share_count = 0
            if share_form:
                share_count = share_form.save(account)
            if membership_form:
                membership_form.save(account)
            invitee.delete()
            membernotification.welcome_co_member(
                account,
                None,
                share_count,
                False
            )
            return redirect('subscription-landing')

    return render(
        request,
        template_name,
        {
            'invitee': invitee,
            'membership_form': membership_form,
            'membership_fee': Config.membership('fee'),
            'share_form': share_form,
            'required_shares_for_membership': Config.membership('required_shares') if share_form else 0,
        },
    )
