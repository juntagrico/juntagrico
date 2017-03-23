# -*- coding: utf-8 -*-

from juntagrico.models import *


class MailTemplateDao:
    def __init__(self):
        pass

    @staticmethod
    def all_templates():
        return MailTemplate.objects.all()

    @staticmethod
    def template_by_id(template_id):
        return MailTemplate.objects.filter(id=template_id)[0]
