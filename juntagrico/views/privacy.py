from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import format_lazy

from juntagrico.config import Config
from juntagrico.entity.member import Member
from juntagrico.forms import subscription
from juntagrico.util.search import full_text_search
from juntagrico.views.manage import MemberArchiveView
from django.utils.translation import gettext_lazy as _


class DeletionRequestView(MemberArchiveView):
    permission_required = ['juntagrico.can_anonymize']
    template_name = 'juntagrico/privacy/deletion_requests.html'
    title = format_lazy(_('Deaktivierte {account}'), account=Config.vocabulary('account_pl'))


@permission_required('juntagrico.can_anonymize')
def anonymize(request, account_id):
    account = get_object_or_404(Member, pk=account_id)
    # catch subscriptions, where for some reason the primary member is not within the subscription members.
    subscriptions = (
        account.subscriptions.all() | account.subscription_primary.all()
    ).exclude(notes='').distinct()

    if request.method == 'POST':
        formset = subscription.NotesFormSet(
            request.POST, queryset=subscriptions
        )

        if request.POST.get('confirm') == 'confirmed' and (not subscriptions.exists() or formset.is_valid()):
            formset.save()
            # todo: prevent anonymization if account has still active anything?
            anonymous = account.anonymize()
            return redirect('manage-account-single', account_id=anonymous.id)
    else:
        formset = subscription.NotesFormSet(queryset=subscriptions)

    return render(
        request,
        'juntagrico/privacy/anonymize.html',
        {'formset': formset, 'account': account},
    )


@permission_required('juntagrico.can_anonymize')
def global_search(request):
    query = request.GET.get('q', '') or request.POST.get('q', '')
    results = []

    if query and len(query) >= 2:  # Minimum 2 characters
        results = full_text_search(query)

    return render(
        request,
        'juntagrico/privacy/search.html',
        {
            'query': query,
            'results': results,
            'total_matches': sum(r['count'] for r in results),
        },
    )
