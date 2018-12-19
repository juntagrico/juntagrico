# encoding: utf-8

from django.conf import settings


class Config:
    def __init__(self):
        pass

    @staticmethod
    def vocabulary(key):
        if hasattr(settings, 'VOCABULARY') and key in settings.VOCABULARY:
            return settings.VOCABULARY[key]
        return {
            'member': 'Mitglied',
            'member_pl': 'Mitglieder',
            'assignment': 'Arbeitseinsatz',
            'assignment_pl': 'Arbeitseinsätze',
            'share': 'Anteilschein',
            'share_pl': 'Anteilscheine',
            'subscription': 'Abo',
            'subscription_pl': 'Abos',
            'co_member': 'Mitabonnent',
            'co_member_pl': 'Mitabonnenten',
            'price': 'Betriebsbeitrag',
            'member_type': 'Mitglied',
            'member_type_pl': 'Mitglieder',
            'depot': 'Depot',
            'depot_pl': 'Depots'
        }[key]

    @staticmethod
    def organisation_name():
        if hasattr(settings, 'ORGANISATION_NAME'):
            return settings.ORGANISATION_NAME
        return 'Juntagrico'

    @staticmethod
    def organisation_name_config():
        if hasattr(settings, 'ORGANISATION_NAME_CONFIG'):
            return settings.ORGANISATION_NAME_CONFIG
        return {'type': '',
                'gender': ''}

    @staticmethod
    def organisation_long_name():
        if hasattr(settings, 'ORGANISATION_LONG_NAME'):
            return settings.ORGANISATION_LONG_NAME
        return 'Juntagrico the best thing in the world'

    @staticmethod
    def organisation_address():
        if hasattr(settings, 'ORGANISATION_ADDRESS'):
            return settings.ORGANISATION_ADDRESS
        return {'name': 'Juntagrico',
                'street': 'Fakestreet',
                'number': '123',
                'zip': '12456',
                'city': 'Springfield',
                'extra': ''}

    @staticmethod
    def organisation_phone():
        return getattr(settings, 'ORGANISATION_PHONE', '')

    @staticmethod
    def organisation_bank_connection():
        if hasattr(settings, 'ORGANISATION_BANK_CONNECTION'):
            return settings.ORGANISATION_BANK_CONNECTION
        return {'PC': '01-123-5',
                'IBAN': 'CH 00 12345 67890 12345 67890 10',
                'BIC': 'BIC12345XX',
                'NAME': 'Juntagrico Bank',
                'ESR': '01-123-45'}

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
        return ''

    @staticmethod
    def bylaws():
        if hasattr(settings, 'BYLAWS'):
            return settings.BYLAWS
        return ''

    @staticmethod
    def mail_template():
        if hasattr(settings, 'MAIL_TEMPLATE'):
            return settings.MAIL_TEMPLATE
        return 'mails/email.html'

    @staticmethod
    def emails(key):
        if hasattr(settings, 'EMAILS'):
            if key in settings.EMAILS:
                return settings.EMAILS[key]
        return {'welcome': 'mails/welcome_mail.txt',
                'co_welcome': 'mails/welcome_added_mail.txt',
                'co_added': 'mails/added_mail.txt',
                'password': 'mails/password_reset_mail.txt',
                'j_reminder': 'mails/job_reminder_mail.txt',
                'j_canceled': 'mails/job_canceled_mail.txt',
                'confirm': 'mails/confirm.txt',
                'j_changed': 'mails/job_time_changed_mail.txt',
                'j_signup': 'mails/job_signup_mail.txt',
                'd_changed': 'mails/depot_changed_mail.txt',
                's_created': 'mails/share_created_mail.txt',
                'n_sub': 'mails/new_subscription.txt',
                's_canceled': 'mails/subscription_canceled_mail.txt',
                'm_canceled': 'mails/membership_canceled_mail.txt',
                'b_share': 'mails/bill_share.txt',
                'b_sub': 'mails/bill_sub.txt',
                'b_esub': 'mails/bill_extrasub.txt'
                }[key]

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
        return '/static/external/bootstrap-4.1.3/css/bootstrap.min.css'

    @staticmethod
    def faq_doc():
        if hasattr(settings, 'FAQ_DOC'):
            return settings.FAQ_DOC
        return ''

    @staticmethod
    def extra_sub_info():
        if hasattr(settings, 'EXTRA_SUB_INFO'):
            return settings.EXTRA_SUB_INFO
        return ''

    @staticmethod
    def activity_area_info():
        if hasattr(settings, 'ACTIVITY_AREA_INFO'):
            return settings.ACTIVITY_AREA_INFO
        return ''

    @staticmethod
    def share_price():
        if hasattr(settings, 'SHARE_PRICE'):
            return settings.SHARE_PRICE
        return '250'

    @staticmethod
    def enable_shares():
        if hasattr(settings, 'ENABLE_SHARES'):
            return settings.ENABLE_SHARES
        return True

    @staticmethod
    def enable_registration():
        if hasattr(settings, 'ENABLE_REGISTRATION'):
            return settings.ENABLE_REGISTRATION
        return True

    @staticmethod
    def base_fee():
        if hasattr(settings, 'BASE_FEE'):
            return settings.BASE_FEE
        return ''

    @staticmethod
    def currency():
        if hasattr(settings, 'CURRENCY'):
            return settings.CURRENCY
        return 'CHF'

    @staticmethod
    def max_units():
        if hasattr(settings, 'MAX_UNIT'):
            return settings.MAX_UNIT
        return -1

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
    def depot_list_generation_days():
        if hasattr(settings, 'DEPOT_LIST_GENERATION_DAYS'):
            return settings.DEPOT_LIST_GENERATION_DAYS
        return [0, 1, 2, 3, 4, 5, 6]

    @staticmethod
    def billing():
        if hasattr(settings, 'BILLING'):
            return settings.BILLING
        return False

    @staticmethod
    def business_year_start():
        if hasattr(settings, 'BUSINESS_YEAR_START'):
            return settings.BUSINESS_YEAR_START
        return {'day': 1, 'month': 1}

    @staticmethod
    def business_year_cancelation_month():
        if hasattr(settings, 'BUSINESS_YEAR_CANCELATION_MONTH'):
            return settings.BUSINESS_YEAR_CANCELATION_MONTH
        return 12

    @staticmethod
    def membership_end_month():
        if hasattr(settings, 'MEMBERSHIP_END_MONTH'):
            return settings.MEMBERSHIP_END_MONTH
        return 6

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
    def default_mailer():
        if hasattr(settings, 'DEFAULT_MAILER'):
            return settings.DEFAULT_MAILER
        return 'juntagrico.util.defaultmailer.Mailer'

    @staticmethod
    def images(key):
        if hasattr(settings, 'IMAGES'):
            if key in settings.IMAGES:
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
