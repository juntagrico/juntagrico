from juntagrico.entity.extrasubs import ExtraSubscriptionCategory


class ExtraSubscriptionCategoryDao:

    @staticmethod
    def all_categories_ordered():
        return ExtraSubscriptionCategory.objects.all()

    @staticmethod
    def categories_for_depot_list_ordered():
        return ExtraSubscriptionCategory.objects.all().filter(depot_list=True)
