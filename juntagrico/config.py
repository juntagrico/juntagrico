# encoding: utf-8

from django.conf import settings


class Config:
    def __init__(self):
        pass

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
    def organisation_long_name():
        if hasattr(settings, 'ORGANISATION_LONG_NAME'):
            return settings.ORGANISATION_LONG_NAME
        return "Juntagrico the best thing in the world"

    @staticmethod
    def organisation_address():
        if hasattr(settings, 'ORGANISATION_ADDRESS'):
            return settings.ORGANISATION_ADDRESS
        return "Juntagrico 123 Fakestreet Springfield"

    @staticmethod
    def organisation_bank_connection():
        if hasattr(settings, 'ORGANISATION_BANK_CONNECTION'):
            return settings.ORGANISATION_BANK_CONNECTION
        return "fakebank something something"

    @staticmethod
    def info_email():
        if hasattr(settings, 'INFO_EMAIL'):
            return settings.INFO_EMAIL
        return "info@juntagrico.juntagrico"

    @staticmethod
    def server_url():
        if hasattr(settings, 'SERVER_URL'):
            return settings.SERVER_URL
        return "www.juntagrico.juntagrico"

    @staticmethod
    def adminportal_name():
        if hasattr(settings, 'ADMINPORTAL_NAME'):
            return settings.ADMINPORTAL_NAME
        return "my.juntagrico"

    @staticmethod
    def adminportal_server_url():
        if hasattr(settings, 'ADMINPORTAL_SERVER_URL'):
            return settings.ADMINPORTAL_SERVER_URL
        return "my.juntagrico.juntagrico"

    @staticmethod
    def business_regulations():
        if hasattr(settings, 'BUSINESS_REGULATIONS'):
            return settings.BUSINESS_REGULATIONS
        return "/static/docs/business_regulations.pdf"

    @staticmethod
    def bylaws():
        if hasattr(settings, 'BYLAWS'):
            return settings.BYLAWS
        return "/static/docs/bylaws.pdf"

    @staticmethod
    def style_sheet():
        if hasattr(settings, 'STYLE_SHEET'):
            return settings.STYLE_SHEET
        return "/static/css/juntagrico.css"

    @staticmethod
    def faq_doc():
        if hasattr(settings, 'FAQ_DOC'):
            return settings.FAQ_DOC
        return "/share/doc/fac.pdf"

    @staticmethod
    def extra_sub_info():
        if hasattr(settings, 'EXTRA_SUB_INFO'):
            return settings.EXTRA_SUB_INFO
        return "/share/doc/extra_sub_info.pdf"

    @staticmethod
    def activity_area_info():
        if hasattr(settings, 'ACTIVITY_AREA_INFO'):
            return settings.ACTIVITY_AREA_INFO
        return "/share/doc/activity_area_info.pdf"

    @staticmethod
    def share_price():
        if hasattr(settings, 'SHARE_PRICE'):
            return settings.SHARE_PRICE
        return "250"

    @staticmethod
    def promoted_job_types():
        if hasattr(settings, 'PROMOTED_JOB_TYPES'):
            return settings.PROMOTED_JOB_TYPES
        return []

    @staticmethod
    def promomted_jobs_amount():
        if hasattr(settings, 'PROMOTED_JOBS_AMOUNT'):
            return settings.PROMOTED_JOBS_AMOUNT
        return 2

    @staticmethod
    def depot_list_cover_sheets():
        if hasattr(settings, 'DEPOT_LIST_COVER_SHEETS'):
            return settings.DEPOT_LIST_COVER_SHEETS
        return 'x'

    @staticmethod
    def depot_list_overviews():
        if hasattr(settings, 'DEPOT_LIST_OVERVIEWS'):
            return settings.DEPOT_LIST_OVERVIEWS
        return 'x'

    @staticmethod
    def depot_list_generation_days():
        if hasattr(settings, 'DEPOT_LIST_GENERATION_DAYS'):
            return settings.DEPOT_LIST_GENERATION_DAYS
        return [1,2,3,4,5,6,7]

    @staticmethod
    def business_year_start():
        if hasattr(settings, 'BUSINESS_YEAR_START'):
            return settings.BUSINESS_YEAR_START
        return {"day":1, "month":1}

    @staticmethod
    def business_year_cancelation_month():
        if hasattr(settings, 'BUSINESS_YEAR_CANCELATION_MONTH'):
            return settings.BUSINESS_YEAR_CANCELATION_MONTH
        return 10

    @staticmethod
    def demo():
        if hasattr(settings, 'DEMO'):
            return settings.DEMO
        return False

    @staticmethod
    def circles(key):
        if hasattr(settings, 'CIRCLES'):
            return settings.CIRCLES[key]
        return {'circle_full': '/static/img/circle_full.png',
            'circle_alomst_full': '/static/img/circle_alomst_full.png',
            'circle_half': 'static/img/circle_half.png',
            'circle_almost_empty': '/static/img/circle_almost_empty.png',
            'circle_empty': '/static/img/circle_empty.png',
            'circle_full_core': '/static/img/circle_full_core.png',
            'circle_x': '/static/img/circle_x.png',
            'circle_y': '/static/img/circle_y.png'
        }[key]




    @staticmethod
    def google_api_key():
        if hasattr(settings, 'GOOGLE_API_KEY'):
            return settings.GOOGLE_API_KEY
        return "GOOGLE_API_KEY"
