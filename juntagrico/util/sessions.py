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


class CreateSubscriptionSessionObject(SessionObject):
    def __init__(self):
        super().__init__()
        self._main_member = None
        self._co_members = []
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
        new_main_member.new_shares = getattr(self._main_member, 'new_shares', None)
        self._main_member = new_main_member

    @property
    def co_members(self):
        return [self.get_co_member(i) for i in range(len(self._co_members))]

    def replace_co_member(self, index, new_co_member):
        new_co_member.new_shares = getattr(self._co_members[index], 'new_shares', None)
        self._co_members[index] = new_co_member

    def get_co_member(self, index):
        co_member = self._co_members[index]
        return co_member

    def add_co_member(self, new_co_member):
        self._co_members.append(new_co_member)

    def remove_co_member(self, index):
        del self._co_members[index]

    def has_co_members(self):
        return len(self._co_members) > 0

    def to_dict(self):
        build_dict = {k: getattr(self, k) for k in ['main_member', 'co_members', 'depot', 'start_date']}
        build_dict['subscriptions'] = {k: v for k, v in self.subscriptions.items() if v > 0}
        return build_dict
