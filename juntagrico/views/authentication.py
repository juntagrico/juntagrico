from django.contrib.auth.views import PasswordChangeView

from juntagrico.forms.auth import JuntagricoPasswordChangeForm


class JuntagricoPasswordChangeView(PasswordChangeView):
    form_class = JuntagricoPasswordChangeForm
    template_name = 'password.html'

    def get_context_data(self, **kwargs):
        kwargs['must_change_password'] = self.request.session.get(
            'must_change_password', False
        )
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session.pop("must_change_password", None)
        return response
