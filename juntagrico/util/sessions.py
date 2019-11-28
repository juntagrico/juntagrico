from juntagrico.config import Config


class SessionObjectManager:
    def __init__(self, request, key, data_type):
        self._request = request
        self._key = key
        if key in request.session:
            self.data = request.session.get(key)
        else:
            self.data = data_type()
            request.session[self._key] = self.data

    def store(self):
        # only store if key exists, otherwise session was flushed
        if self._key in self._request.session and not self.data.cleared:
            self._request.session[self._key] = self.data


class SessionObject:
    def __init__(self):
        self.cleared = False

    def clear(self):
        self.cleared = True
        self.__init__()


class CSSessionObject(SessionObject):
    def __init__(self):
        super().__init__()
        self._main_member = None
        self._co_members = []
        self.co_members_done = False
        self.subscriptions = {}
        self.depot = None
        self.start_date = None
        self.edit = False

    @property
    def main_member(self):
        return self._main_member

    @main_member.setter
    def main_member(self, new_main_member):
        # transfer previously selected shares
        new_main_member.new_shares = getattr(self._main_member, 'new_shares', 0)
        self._main_member = new_main_member

    @property
    def co_members(self):
        return self._co_members.copy()

    def get_co_member(self, index):
        co_member = self._co_members[index]
        return co_member

    def add_co_member(self, new_co_member):
        new_co_member.new_shares = 0
        self._co_members.append(new_co_member)

    def remove_co_member(self, index):
        del self._co_members[index]

    def has_co_members(self):
        return len(self._co_members) > 0

    def get_co_member_shares(self):
        return sum([getattr(co_member, 'new_shares', 0) for co_member in self.co_members])

    def subscription_size(self):
        return sum([sub_type.size.units * amount for sub_type, amount in self.subscriptions.items()])

    def required_shares(self):
        return sum([sub_type.shares * amount for sub_type, amount in self.subscriptions.items()])

    def to_dict(self):
        build_dict = {k: getattr(self, k) for k in ['main_member', 'co_members', 'depot', 'start_date']}
        build_dict['subscriptions'] = {k: v for k, v in self.subscriptions.items() if v > 0}
        return build_dict

    def count_shares(self):
        shares = {
            'existing_main_member': len(self.main_member.active_shares),
            'existing_co_member': sum([len(co_member.active_shares) for co_member in self.co_members]),
            'total_required': max(self.required_shares(), 1)
        }
        shares['remaining_required'] = max(0, shares['total_required'] - max(0, shares['existing_main_member'] + shares['existing_co_member']))
        return shares

    def evaluate_ordered_shares(self, shares=None):
        if not Config.enable_shares():  # skip if no shares are needed
            return True
        shares = shares or self.count_shares()
        # count new shares
        new_main_member = getattr(self.main_member, 'new_shares', 0)
        new_co_members = self.get_co_member_shares()
        # evaluate
        return shares['existing_main_member'] + new_main_member > 0\
            and new_main_member + new_co_members >= shares['remaining_required']

    def next_page(self):
        has_subs = self.subscription_size() > 0
        if not self.subscriptions:
            return 'cs-subscription'
        elif has_subs and not self.depot:
            return 'cs-depot'
        elif has_subs and not self.start_date:
            return 'cs-start'
        elif has_subs and not self.co_members_done:
            return 'cs-co-members'
        elif not self.evaluate_ordered_shares():
            return 'cs-shares'
        return 'cs-summary'
