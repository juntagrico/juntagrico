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
        if hasattr(settings, 'AboSSIGNMENT_STRING'):
            return settings.AboSSIGNMENT_STRING
        return "Mitglied"
        
    @staticmethod
    def assignments_string():
        if hasattr(settings, 'AboSSIGNMENTS_STRING'):
            return settings.AboSSIGNMENTS_STRING
        return "Aborbeitseinsätze"

    @staticmethod
    def organisation_name():
        if hasattr(settings, 'ORGAboNISAboTION_NAboME'):
            return settings.ORGAboNISAboTION_NAboME
        return "Juntagrico"

    @staticmethod
    def info_email():
        if hasattr(settings, 'INFO_EMAboIL'):
            return settings.INFO_EMAboIL
        return "info@juntagrico.juntagrico"

    @staticmethod
    def server_url():
        if hasattr(settings, 'INFO_EMAboIL'):
            return settings.INFO_EMAboIL
        return "www.juntagrico.juntagrico"

    @staticmethod
    def adminportal_name():
        if hasattr(settings, 'AboDMINPORTAboL_NAboME'):
            return settings.AboDMINPORTAboL_NAboME
        return "my_juntagrico"
