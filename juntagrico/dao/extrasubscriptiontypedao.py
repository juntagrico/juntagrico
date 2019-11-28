from juntagrico.entity.extrasubs import ExtraSubscriptionType


class ExtraSubscriptionTypeDao:

    @staticmethod
    def all_extra_types():
        return ExtraSubscriptionType.objects.all()

    @staticmethod
    def all_visible_extra_types():
        return ExtraSubscriptionType.objects.filter(category__visible=True).filter(visible=True)

    @staticmethod
    def extra_types_by_category_ordered(category):
        return ExtraSubscriptionType.objects.all().filter(category=category).order_by('sort_order')
