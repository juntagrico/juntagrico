from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from juntagrico.config import Config
from juntagrico.forms.membership import CreateMembershipForm, CreateMembershipWithSharesForm


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
