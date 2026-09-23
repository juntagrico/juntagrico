from juntagrico.entity.jobs import ActivityArea


class ActivityAreaDao:
    @staticmethod
    def all_visible_areas_ordered():
        return ActivityArea.objects.filter(hidden=False).order_by('-core', 'name')

    @staticmethod
    def all_auto_add_members_areas():
        return ActivityArea.objects.filter(auto_add_new_members=True)

    @staticmethod
    def all_core_areas():
        print('ActivityAreaDao.all_core_areas is deprecated: Use ActivityArea.objects.filter(core=True) instead')
        return ActivityArea.objects.filter(core=True)
