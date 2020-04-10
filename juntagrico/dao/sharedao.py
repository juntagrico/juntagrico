from juntagrico.entity.share import Share


class ShareDao:

    @staticmethod
    def paid_shares(subscription):
        return Share.objects.filter(member__in=subscription.recipients).filter(paid_date__isnull=False).filter(
            cancelled_date__isnull=True)

    @staticmethod
    def all_shares_subscription(subscription):
        return Share.objects.filter(member__in=subscription.recipients_all).filter(
            cancelled_date__isnull=True)

    @staticmethod
    def unpaid_shares(member):
        return Share.objects.filter(member=member).filter(paid_date__isnull=True)

    @staticmethod
    def canceled_shares():
        return Share.objects.filter(cancelled_date__isnull=False).filter(
            payback_date__isnull=True)
