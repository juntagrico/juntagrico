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
