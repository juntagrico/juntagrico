# -*- coding: utf-8 -*-

from juntagrico.models import *


class ListMessageDao:

    @staticmethod
    def all_active():
        return ListMessage.objects.filter(active=True).order_by('sort_order')
