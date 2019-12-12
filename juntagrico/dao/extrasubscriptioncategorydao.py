from juntagrico.entity.extrasubs import ExtraSubscriptionCategory


class ExtraSubscriptionCategoryDao:

    @staticmethod
    def all_categories_ordered():
        return ExtraSubscriptionCategory.objects.all().order_by('sort_order')
