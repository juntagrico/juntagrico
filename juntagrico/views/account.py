from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _, ngettext

from juntagrico.config import Config
from juntagrico.forms.account import CancellationForm
from juntagrico.util.temporal import next_membership_end_date


@login_required
def cancellation(request):
    account = request.user.member
    if request.method == 'POST':
        form = CancellationForm(request.POST, instance=account)
        if form.is_valid():
            summary = form.save()
            if summary['subscription']:
                messages.success(request, _('{subscription} gekündigt').format(subscription=Config.vocabulary('subscription')))
            if summary['co_membership']:
                messages.success(request, _('{subscription} verlassen').format(subscription=Config.vocabulary('subscription')))
            if 'activity_area' in summary:
                messages.success(request, _('Tätigkeitsbereiche verlassen'))
            if 'membership' in summary:
                messages.success(request, _('{membership} gekündigt').format(membership=Config.vocabulary('membership')))
            if 'share' in summary:
                messages.success(request, ngettext(
                        '{num} {share} gekündigt',
                        '{num} {shares} gekündigt',
                        summary['share']
                    ).format(
                        num=summary['share'],
                        share=Config.vocabulary('share'),
                        shares=Config.vocabulary('share_pl'),
                    )
                )
            if 'account' in summary:
                messages.success(request, _('{account} gekündigt').format(account=Config.vocabulary('account')))

            return redirect('subscription-landing')
    else:
        form = CancellationForm(instance=account)

    return render(request, 'juntagrico/my/cancellation.html', {
        'form': form,
        'next_membership_end_date': next_membership_end_date(),
    })
