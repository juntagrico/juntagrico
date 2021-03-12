from juntagrico.entity.depot import Depot


class DepotDao:

    @staticmethod
    def all_depots():
        return Depot.objects.all()

    @staticmethod
    def all_depots_ordered():
        return Depot.objects.all()

    @staticmethod
    def all_visible_depots():
        return Depot.objects.all().filter(visible=True)

    @staticmethod
    def all_depots_for_list():
        return Depot.objects.all().filter(depot_list=True)

    @staticmethod
    def depots_for_contact(member):
        return Depot.objects.filter(contact=member)

    @staticmethod
    def depot_by_id(identifier):
        return Depot.objects.all().filter(id=identifier)[0]

    @staticmethod
    def distinct_weekdays_for_depot_list():
        return Depot.objects.all().filter(depot_list=True).order_by('weekday').values('weekday').distinct()
