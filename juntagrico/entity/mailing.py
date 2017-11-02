# encoding: utf-8

from django.db import models

class MailTemplate(models.Model):
    '''
    Mail template for rendering
    '''
    name = models.CharField('Name', max_length=100, unique=True)
    template = models.TextField('Template', max_length=1000, default='')
    code = models.TextField('Code', max_length=1000, default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'MailTemplate'
        verbose_name_plural = 'MailTemplates'
        permissions = (('can_load_templates', 'Benutzer kann Templates laden'),)