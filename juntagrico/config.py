# encoding: utf-8

from django.conf import settings

class Config:

    @staticmethod
    def member_string():
        if hasattr(settings, 'MEMBER_STRING'):
            return settings.MEMBER_STRING
        return "Mitglied"
        
    @staticmethod
    def members_string():
        if hasattr(settings, 'MEMBERS_STRING'):
            return settings.MEMBERS_STRING
        return "Mitglieder"
        
    @staticmethod
    def assignment_string():
        if hasattr(settings, 'ASSIGNMENT_STRING'):
            return settings.ASSIGNMENT_STRING
        return "Mitglied"
        
    @staticmethod
    def assignments_string():
        if hasattr(settings, 'ASSIGNMENTS_STRING'):
            return settings.ASSIGNMENTS_STRING
        return "Arbeitseinsätze"

    @staticmethod
    def organisation_name():
        if hasattr(settings, 'ORGANISATION_NAME'):
            return settings.ORGANISATION_NAME
        return "Juntagrico"

    @staticmethod
    def info_email():
        if hasattr(settings, 'INFO_EMAIL'):
            return settings.INFO_EMAIL
        return "info@juntagrico.juntagrico"

    @staticmethod
    def server_url():
        if hasattr(settings, 'INFO_EMAIL'):
            return settings.INFO_EMAIL
        return "www.juntagrico.juntagrico"

    @staticmethod
    def adminportal_name():
        if hasattr(settings, 'ADMINPORTAL_NAME'):
            return settings.ADMINPORTAL_NAME
        return "my_juntagrico"
