from juntagrico.entity.listmessage import ListMessage


class ListMessageDao:

    @staticmethod
    def all_active():
        return ListMessage.objects.filter(active=True).order_by('sort_order')
