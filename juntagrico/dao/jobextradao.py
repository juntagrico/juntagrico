# -*- coding: utf-8 -*-
from django.utils import timezone

from juntagrico.models import *
from juntagrico.config import Config


class JobExtraDao:

    @staticmethod
    def all_job_extras():
        return JobExtra.objects.all()