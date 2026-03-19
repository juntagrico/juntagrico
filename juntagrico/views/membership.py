from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from juntagrico.config import Config
from juntagrico.forms import CoopMemberCancellationForm, NonCoopMemberCancellationForm
from juntagrico.forms.signup import CreateMembershipForm, CreateMembershipWithSharesForm
from juntagrico.util.temporal import next_membership_end_date


@login_required
def create(request):
    account = request.user.member

    if Config.enable_shares():
        form_class = CreateMembershipWithSharesForm.create(
            Config.membership('required_shares'),
            account.usable_shares.count()
        )
    else:
        form_class = CreateMembershipForm

    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            form.save(account)
            return redirect('profile')
    else:
        form = form_class()

    return render(request, 'juntagrico/my/membership/create.html', {
        'form': form,
        'required_shares': Config.membership('required_shares'),
        'membership_fee': Config.membership('fee'),
    })


@login_required
def cancel(request):
    member = request.user.member
    # Check if membership can be canceled
    asc = member.usable_shares_count
    sub = member.subscription_current
    f_sub = member.subscription_future
    future_active = f_sub is not None and not f_sub.canceled
    current_active = sub is not None and not sub.canceled
    future = future_active and f_sub.share_overflow - asc < 0
    current = current_active and sub.share_overflow - asc < 0
    share_error = future or current
    can_cancel = not share_error and not future_active and not current_active
    # considering unpaid shares as well, as they might have been paid but not yet updated in the system.
    # Then IBAN is needed to pay it back.
    coop_member = member.usable_shares_count > 0
    if coop_member:
        form_type = CoopMemberCancellationForm
    else:
        form_type = NonCoopMemberCancellationForm
    if can_cancel and request.method == 'POST':
        form = form_type(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = form_type(instance=member)
    renderdict = {
        'coop_member': coop_member,
        'end_date': next_membership_end_date(),
        'member': member,
        'can_cancel': can_cancel,
        'share_error': share_error,
        'form': form
    }
    return render(request, 'juntagrico/my/membership/cancel.html', renderdict)
