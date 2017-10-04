# -*- coding: utf-8 -*-

from juntagrico.models import *


class MailTemplateDao:

    @staticmethod
    def all_templates():
        return MailTemplate.objects.all()

    @staticmethod
    def template_by_id(template_id):
        return MailTemplate.objects.filter(id=template_id)[0]
