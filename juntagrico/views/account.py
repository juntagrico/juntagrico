from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from juntagrico.forms.account import CancellationForm


@login_required
def cancellation(request):
    account = request.user.member
    if request.method == 'POST':
        form = CancellationForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect('subscription-landing')
    else:
        form = CancellationForm(instance=account)

    return render(request, 'juntagrico/my/cancellation.html', {
        'form': form,
    })
