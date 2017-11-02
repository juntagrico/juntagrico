# encoding: utf-8

from django.conf import settings


class Config:
    def __init__(self):
        pass

    @staticmethod
    def member_string():
        if hasattr(settings, 'MEMBER_STRING'):
            return settings.MEMBER_STRING
        return 'Mitglied'

    @staticmethod
    def members_string():
        if hasattr(settings, 'MEMBERS_STRING'):
            return settings.MEMBERS_STRING
        return 'Mitglieder'

    @staticmethod
    def assignment_string():
        if hasattr(settings, 'ASSIGNMENT_STRING'):
            return settings.ASSIGNMENT_STRING
        return 'Mitglied'

    @staticmethod
    def assignments_string():
        if hasattr(settings, 'ASSIGNMENTS_STRING'):
            return settings.ASSIGNMENTS_STRING
        return 'Arbeitseinsätze'

    @staticmethod
    def organisation_name():
        if hasattr(settings, 'ORGANISATION_NAME'):
            return settings.ORGANISATION_NAME
        return 'Juntagrico'

    @staticmethod
    def organisation_long_name():
        if hasattr(settings, 'ORGANISATION_LONG_NAME'):
            return settings.ORGANISATION_LONG_NAME
        return 'Juntagrico the best thing in the world'

    @staticmethod
    def organisation_address():
        if hasattr(settings, 'ORGANISATION_ADDRESS'):
            return settings.ORGANISATION_ADDRESS
        return {'name':'Juntagrico', 
                'street' : 'Fakestreet',
                'number' : '123',
                'zip' : '12456',
                'city' : 'Springfield',
                'extra' : ''}

    @staticmethod
    def organisation_bank_connection():
        if hasattr(settings, 'ORGANISATION_BANK_CONNECTION'):
            return settings.ORGANISATION_BANK_CONNECTION
        return {'PC' : '01-123-5',
                'IBAN' : 'CH 00 12345 67890 12345 67890 10',
                'BIC' : 'BIC12345XX',
                'NAME' : 'Juntagrico Bank',
                'ESR' : '01-123-45'}

    @staticmethod
    def info_email():
        if hasattr(settings, 'INFO_EMAIL'):
            return settings.INFO_EMAIL
        return 'info@juntagrico.juntagrico'

    @staticmethod
    def server_url():
        if hasattr(settings, 'SERVER_URL'):
            return settings.SERVER_URL
        return 'www.juntagrico.juntagrico'

    @staticmethod
    def adminportal_name():
        if hasattr(settings, 'ADMINPORTAL_NAME'):
            return settings.ADMINPORTAL_NAME
        return 'my.juntagrico'

    @staticmethod
    def adminportal_server_url():
        if hasattr(settings, 'ADMINPORTAL_SERVER_URL'):
            return settings.ADMINPORTAL_SERVER_URL
        return 'my.juntagrico.juntagrico'

    @staticmethod
    def business_regulations():
        if hasattr(settings, 'BUSINESS_REGULATIONS'):
            return settings.BUSINESS_REGULATIONS
        return '/static/docs/business_regulations.pdf'

    @staticmethod
    def bylaws():
        if hasattr(settings, 'BYLAWS'):
            return settings.BYLAWS
        return '/static/docs/bylaws.pdf'

    @staticmethod
    def mail_template():
        if hasattr(settings, 'MAIL_TEMPLATE'):
            return settings.MAIL_TEMPLATE
        return 'mails/email.html'

    @staticmethod
    def style_sheet():
        if hasattr(settings, 'STYLE_SHEET'):
            return settings.STYLE_SHEET
        return '/static/css/personal.css'

    @staticmethod
    def favicon():
        if hasattr(settings, 'FAVICON'):
            return settings.FAVICON
        return '/static/img/favicon.ico'

    @staticmethod
    def bootstrap():
        if hasattr(settings, 'BOOTSTRAP'):
            return settings.BOOTSTRAP
        return '/static/external/bootstrap-3.3.1/css/bootstrap.min.css'

    @staticmethod
    def faq_doc():
        if hasattr(settings, 'FAQ_DOC'):
            return settings.FAQ_DOC
        return '/static/doc/fac.pdf'

    @staticmethod
    def extra_sub_info():
        if hasattr(settings, 'EXTRA_SUB_INFO'):
            return settings.EXTRA_SUB_INFO
        return '/static/doc/extra_sub_info.pdf'

    @staticmethod
    def activity_area_info():
        if hasattr(settings, 'ACTIVITY_AREA_INFO'):
            return settings.ACTIVITY_AREA_INFO
        return '/static/doc/activity_area_info.pdf'

    @staticmethod
    def share_price():
        if hasattr(settings, 'SHARE_PRICE'):
            return settings.SHARE_PRICE
        return '250'

    @staticmethod
    def currency():
        if hasattr(settings, 'CURRENCY'):
            return settings.CURRENCY
        return 'CHF'

    @staticmethod
    def assignment_unit():
        if hasattr(settings, 'ASSIGNMENT_UNIT'):
            return settings.ASSIGNMENT_UNIT
        return 'ENTITY'

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
    def billing():
        if hasattr(settings, 'BILLING'):
            return settings.BILLING
        return False

    @staticmethod
    def business_year_start():
        if hasattr(settings, 'BUSINESS_YEAR_START'):
            return settings.BUSINESS_YEAR_START
        return {'day':1, 'month':1}

    @staticmethod
    def business_year_cancelation_month():
        if hasattr(settings, 'BUSINESS_YEAR_CANCELATION_MONTH'):
            return settings.BUSINESS_YEAR_CANCELATION_MONTH
        return 12

    @staticmethod
    def demouser():
        if hasattr(settings, 'DEMO_USER'):
            return settings.DEMO_USER
        return ''

    @staticmethod
    def demopwd():
        if hasattr(settings, 'DEMO_PWD'):
            return settings.DEMO_PWD
        return ''

    @staticmethod
    def images(key):
        if hasattr(settings, 'IMAGES'):
            return settings.IMAGES[key]
        return {'status_100': '/static/img/status_100.png',
            'status_75': '/static/img/status_75.png',
            'status_50': '/static/img/status_50.png',
            'status_25': '/static/img/status_25.png',
            'status_0': '/static/img/status_0.png',
            'single_full': '/static/img/single_full.png',
            'single_empty': '/static/img/single_empty.png',
            'single_core': '/static/img/single_core.png',
            'core': '/static/img/core.png'
        }[key]




    @staticmethod
    def google_api_key():
        if hasattr(settings, 'GOOGLE_API_KEY'):
            return settings.GOOGLE_API_KEY
        return 'GOOGLE_API_KEY'
