from django.db import transaction

from juntagrico.entity.depot import Depot
from juntagrico.entity.member import Member
from juntagrico.entity.subtypes import SubscriptionType
from juntagrico.forms import RegisterMemberForm, ShareOrderForm, CoMemberBaseForm, StartDateForm
from juntagrico.mailer import adminnotification, membernotification
from juntagrico.util.management import create_share, create_subscription_parts


class SessionManager:
    session_name = ''

    def __init__(self, request):
        self.request = request
        if self.session_name not in request.session:
            request.session[self.session_name] = {}
        self.data = request.session[self.session_name]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.request.session[self.session_name] = self.data

    def append(self, key, value):
        if key not in self.data or not isinstance(self.data[key], list):
            self.data[key] = [value]
        else:
            self.data[key].append(value)
        self.request.session[self.session_name] = self.data

    def remove(self, key, index):
        self.data[key].pop(index)
        self.request.session[self.session_name] = self.data

    def replace(self, key, index, value):
        self.data[key][index] = value
        self.request.session[self.session_name] = self.data

    def clear(self):
        self.data = self.request.session[self.session_name] = {}


class SignupManager(SessionManager):
    session_name = 'signup'

    def _main_member_form(self):
        form = RegisterMemberForm(self.data.get('main_member', {}))
        form.full_clean()
        return form

    def main_member(self):
        return self._main_member_form().instance

    def comment(self):
        return self.data.get('main_member', {}).get('comment', '')

    def has_parts(self):
        return any(self.get('subscriptions', {}).values())

    def subscriptions(self):
        """
        :return: dict of subscription_types -> amount, where selected amount > 0
        """
        subscription = self.get('subscriptions', {})
        sub_types = SubscriptionType.objects.filter(id__in=subscription.keys())
        return {sub_type: subscription[str(sub_type.id)] for sub_type in sub_types if subscription[str(sub_type.id)]}

    def depot(self):
        if (depot_id := self.data.get('depot', None)) is not None:
            return Depot.objects.get(id=depot_id)

    def co_members(self):
        co_members = []
        for c in self.get('co_members', []):
            if isinstance(c, str):
                co_member = Member.objects.get(email=c)
                co_members.append((str(co_member), co_member.active_shares_count))
            else:
                co_members.append((c['first_name'] + ' ' + c['last_name'], 0))
        return co_members

    def required_shares(self):
        return sum([s.shares * amount for s, amount in self.subscriptions().items()])

    def existing_shares(self):
        return self.request.user.member.active_shares_count if self.request.user.is_authenticated else 0

    def shares_ok(self):
        return ShareOrderForm(self.required_shares(), self.existing_shares(), self.co_members(), data=self.get('shares')).is_valid()

    def get_next_page(self):
        """identify next page, based on what information is still missing
        """
        if self.request.user.is_authenticated:
            if not self.request.user.member.can_order_subscription:
                return 'subscription-landing'
        elif not self.get('main_member'):
            return 'signup'
        has_parts = self.has_parts()
        if not self.get('subscriptions'):
            return 'cs-subscription'
        elif has_parts and self.get('depot') is None:
            return 'cs-depot'
        elif has_parts and not self.get('start_date'):
            return 'cs-start'
        elif has_parts and not self.get('co_members_done'):
            return 'cs-co-members'
        elif not self.shares_ok():
            return 'cs-shares'
        return 'cs-summary'

    @transaction.atomic
    def apply(self):
        """ create all elements from data the collected data
        :return the new main member
        """
        # create member
        if self.request.user.is_authenticated:
            member = self.request.user.member
            password = None
        else:
            member_form = self._main_member_form()
            member_form.instance.comment = self.get('comment', '')  # inject comment to be available in admin notification
            member = member_form.save()
            password = member.set_password()

        # create co-members
        co_members = {}
        for co_member_data in self.get('co_members', []):
            if isinstance(co_member_data, str):
                co_members[Member.objects.get(email=co_member_data)] = [None]
            else:
                co_member = CoMemberBaseForm(co_member_data).save()
                co_members[co_member] = [co_member.set_password()]

        # create shares (notifies member and admin)
        shares = self.get('shares')
        create_share(member, int(shares['of_member']))
        for i, co_member in enumerate(co_members.keys()):
            shares_of_co_member = int(shares[f'of_co_member[{i}]'])
            co_members[co_member].append(shares_of_co_member)
            create_share(co_member, shares_of_co_member)

        # create subscription
        subscription = None
        if self.has_parts():
            # create instance
            subscription = StartDateForm({'start_date': self.get('start_date')}).save(commit=False)
            subscription.depot = self.depot()
            subscription.save()
            # let members join it
            member.join_subscription(subscription, primary=True)
            for co_member in co_members.keys():
                co_member.join_subscription(subscription)
            # add parts
            create_subscription_parts(subscription, self.subscriptions())
            # notify admin
            adminnotification.subscription_created(subscription, self.get('comment', ''))

        # send welcome email to members and co-members
        if password:
            membernotification.welcome(member, password)
        for co_member, details in co_members.items():
            password, shares = details
            membernotification.welcome_co_member(co_member, password, shares, new=password is not None)

        self.clear()
        return member
