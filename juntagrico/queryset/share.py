from polymorphic.query import PolymorphicQuerySet


class ShareQueryset(PolymorphicQuerySet):
    def active(self):
        return self.filter(paid_date__isnull=False).filter(payback_date__isnull=True)

    def unpaid(self):
        return self.filter(paid_date__isnull=True)

    def usable(self):
        """ :return: shares that have been ordered (i.e. created) and not cancelled yet
        """
        return self.filter(cancelled_date__isnull=True)
