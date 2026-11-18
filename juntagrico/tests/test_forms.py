from django.core.exceptions import ValidationError

from juntagrico.forms import SubscriptionExtraPartSelectForm, SubscriptionPartBaseForm, \
    SubscriptionPartSelectForm, SubscriptionPartSelectRequiredForm
from . import JuntagricoTestCase


def reject_all(form):
    raise ValidationError('rejected by validator', code='rejected_by_validator')


class SubscriptionPartSelectFormValidatorTests(JuntagricoTestCase):
    def setUp(self):
        super().setUp()
        # addons register validators on the base form
        self.validators = SubscriptionPartBaseForm.validators
        self.validators.append(reject_all)

    def tearDown(self):
        self.validators.remove(reject_all)
        super().tearDown()

    def assertValidatorRuns(self, form_class):
        form = form_class({}, {f'amount[{self.sub_type.pk}]': 1})
        self.assertFalse(form.is_valid())
        self.assertIn('rejected_by_validator', [e.code for e in form.non_field_errors().as_data()])

    def test_select_form(self):
        self.assertValidatorRuns(SubscriptionPartSelectForm)

    def test_select_required_form(self):
        self.assertValidatorRuns(SubscriptionPartSelectRequiredForm)

    def test_extra_select_form(self):
        self.assertValidatorRuns(SubscriptionExtraPartSelectForm)

    def test_select_required_form_without_selection(self):
        form = SubscriptionPartSelectRequiredForm({}, {f'amount[{self.sub_type.pk}]': 0})
        self.assertFalse(form.is_valid())
        self.assertEqual([e.code for e in form.non_field_errors().as_data()], ['selection_error'])
