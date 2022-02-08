from django.conf import settings
from django.contrib.sites.models import Site
from django.templatetags.static import static
from django.utils.translation import gettext as _


def _get_setting(setting_key, default: object = ''):
    return lambda: getattr(settings, setting_key, default() if callable(default) else default)


def _get_setting_with_key(setting_key, default):
    def inner(key):
        if hasattr(settings, setting_key) and key in getattr(settings, setting_key):
            return getattr(settings, setting_key)[key]
        return (default() if callable(default) else default)[key]

    return inner


class Config:
    # organisation settings
    vocabulary = _get_setting_with_key(
        'VOCABULARY',
        {
            'member': _('Mitglied'),
            'member_pl': _('Mitglieder'),
            'assignment': _('Arbeitseinsatz'),
            'assignment_pl': _('Arbeitseinsätze'),
            'share': _('Anteilschein'),
            'share_pl': _('Anteilscheine'),
            'subscription': _('Abo'),
            'subscription_pl': _('Abos'),
            'co_member': _('MitabonnentIn'),
            'co_member_pl': _('MitabonnentInnen'),
            'price': _('Betriebsbeitrag'),
            'member_type': _('Mitglied'),
            'member_type_pl': _('Mitglieder'),
            'depot': _('Depot'),
            'depot_pl': _('Depots'),
            'package': _('Tasche'),
        }
    )
    organisation_name = _get_setting('ORGANISATION_NAME', 'Juntagrico')
    organisation_name_config = _get_setting('ORGANISATION_NAME_CONFIG', {'type': '', 'gender': ''})
    organisation_long_name = _get_setting('ORGANISATION_LONG_NAME', 'Juntagrico the best thing in the world')
    organisation_address = _get_setting(
        'ORGANISATION_ADDRESS',
        {
            'name': 'Juntagrico',
            'street': 'Fakestreet',
            'number': '123',
            'zip': '12456',
            'city': 'Springfield',
            'extra': ''
        }
    )
    organisation_phone = _get_setting('ORGANISATION_PHONE')
    organisation_bank_connection = _get_setting(
        'ORGANISATION_BANK_CONNECTION',
        {
            'PC': '01-123-5',
            'IBAN': 'CH 00 12345 67890 12345 67890 10',
            'BIC': 'BIC1234500',
            'NAME': 'Juntagrico Bank',
        }
    )
    share_price = _get_setting('SHARE_PRICE', '250')
    business_regulations = _get_setting('BUSINESS_REGULATIONS')
    bylaws = _get_setting('BYLAWS')
    gdpr_info = _get_setting('GDPR_INFO')
    faq_doc = _get_setting('FAQ_DOC')
    extra_sub_info = _get_setting('EXTRA_SUB_INFO')
    activity_area_info = _get_setting('ACTIVITY_AREA_INFO')
    enable_shares = _get_setting('ENABLE_SHARES', True)
    enable_registration = _get_setting('ENABLE_REGISTRATION', True)
    base_fee = _get_setting('BASE_FEE')
    currency = _get_setting('CURRENCY', 'CHF')
    assignment_unit = _get_setting('ASSIGNMENT_UNIT', 'ENTITY')
    promoted_job_types = _get_setting('PROMOTED_JOB_TYPES', [])
    promomted_jobs_amount = _get_setting('PROMOTED_JOBS_AMOUNT', 2)
    depot_list_generation_days = _get_setting('DEPOT_LIST_GENERATION_DAYS', [0, 1, 2, 3, 4, 5, 6])
    default_depot_list_generators = _get_setting('DEFAULT_DEPOTLIST_GENERATORS', ['juntagrico.util.depot_list.default_depot_list_generation'])
    business_year_start = _get_setting('BUSINESS_YEAR_START', {'day': 1, 'month': 1})
    business_year_cancelation_month = _get_setting('BUSINESS_YEAR_CANCELATION_MONTH', 12)
    membership_end_month = _get_setting('MEMBERSHIP_END_MONTH', 6)
    cookie_consent = _get_setting_with_key(
        'COOKIE_CONSENT',
        lambda: {
            'text': _('{} verwendet folgende Cookies: session, csfr, cookieconsent.').format(
                Site.objects.get_current().name),
            'confirm_text': _('einverstanden'),
            'link_text': _('Hier findest du mehr zum Thema'),
            'url': '/my/cookies'
        }
    )
    sub_overview_format = _get_setting_with_key(
        'SUB_OVERVIEW_FORMAT',
        lambda: {
            'delimiter': '|',
            'format': '{product}:{size}:{type}={amount}'
        }
    )

    # url and email settings
    info_email = _get_setting('INFO_EMAIL', 'info@juntagrico.juntagrico')
    server_url = _get_setting('SERVER_URL', 'www.juntagrico.juntagrico')
    default_mailer = _get_setting('DEFAULT_MAILER', 'juntagrico.util.defaultmailer.Mailer')
    from_filter = _get_setting_with_key('FROM_FILTER',
                                        {
                                            'filter_expression': '.*',
                                            'replacement_from': ''
                                        })

    # template settings
    mail_template = _get_setting('MAIL_TEMPLATE', 'mails/email.html')
    emails = _get_setting_with_key(
        'EMAILS',
        {
            'welcome': 'mails/member/member_welcome.txt',
            'co_welcome': 'mails/member/co_member_welcome.txt',
            'co_added': 'mails/member/co_member_added.txt',
            'password': 'mails/member/password_reset.txt',
            'confirm': 'mails/member/email_confirm.txt',
            'j_reminder': 'mails/member/job_reminder.txt',
            'j_canceled': 'mails/member/job_canceled.txt',
            'j_changed': 'mails/member/job_time_changed.txt',
            'j_signup': 'mails/member/job_signup.txt',
            'd_changed': 'mails/member/depot_changed.txt',
            's_created': 'mails/member/share_created.txt',
            'm_left_subscription': 'mails/member/co_member_left_subscription.txt',
            'n_sub': 'mails/admin/subscription_created.txt',
            's_canceled': 'mails/admin/subscription_canceled.txt',
            'a_share_created': 'mails/admin/share_created.txt',
            'a_share_canceled': 'mails/admin/share_canceled.txt',
            'a_subpart_created': 'mails/admin/subpart_created.txt',
            'a_subpart_canceled': 'mails/admin/subpart_canceled.txt',
            'a_member_created': 'mails/admin/member_created.txt',
            'a_depot_list_generated': 'mails/admin/depot_list_generated.txt',
            'm_canceled': 'mails/admin/member_canceled.txt',
        }
    )
    favicon = _get_setting('FAVICON', static('juntagrico/img/favicon.ico'))
    bootstrap = _get_setting('BOOTSTRAP', static('juntagrico/external/bootstrap-4.3.1/css/bootstrap.min.css'))
    styles = _get_setting_with_key('STYLES', {'template': '', 'static': []})
    scripts = _get_setting_with_key('SCRIPTS', {'template': '', 'static': []})
    images = _get_setting_with_key(
        'IMAGES',
        {
            'status_100': static('juntagrico/img/status_100.png'),
            'status_75': static('juntagrico/img/status_75.png'),
            'status_50': static('juntagrico/img/status_50.png'),
            'status_25': static('juntagrico/img/status_25.png'),
            'status_0': static('juntagrico/img/status_0.png'),
            'single_full': static('juntagrico/img/single_full.png'),
            'single_empty': static('juntagrico/img/single_empty.png'),
            'single_core': static('juntagrico/img/single_core.png'),
            'core': static('juntagrico/img/core.png')
        }
    )
    mailer_richtext_options = _get_setting('MAILER_RICHTEXT_OPTIONS', {})

    # demo settings
    demouser = _get_setting('DEMO_USER')
    demopwd = _get_setting('DEMO_PWD')
