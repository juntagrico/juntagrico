import sys
from typing import Any

from django.conf import settings
from django.contrib.sites.models import Site
from django.templatetags.static import static
from django.utils.translation import gettext, gettext_lazy as _

from juntagrico import defaults


FIRST_JOB_NOTIFICATION_MAP = {
    'overall': 'first_job_subscribed',
    'per_area': 'first_job_in_area_subscribed',
    'per_type': 'first_job_in_type_subscribed',
}


def _get_setting(setting_key, default: Any = ''):
    return lambda: getattr(settings, setting_key, default() if callable(default) else default)


def _get_setting_with_key(setting_key, default):
    def inner(key, fallback=None):
        if hasattr(settings, setting_key) and key in getattr(settings, setting_key):
            return getattr(settings, setting_key)[key]
        d = default.get(key, fallback)
        return d() if callable(d) else d

    return inner


def fallback_static(path):
    try:
        return static(path)
    except ValueError:
        return path


def v_format(text, key):
    return lambda: text.format(**{key: Config.vocabulary(key)})


class Config:
    # organisation settings
    vocabulary = _get_setting_with_key(
        'VOCABULARY',
        {
            'account': _('Konto'),
            'account_pl': _('Konten'),
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
            'membership': _('Mitgliedschaft'),
            'membership_pl': _('Mitgliedschaften'),
            'depot': _('Depot'),
            'depot_pl': _('Depots'),
            'package': _('Tasche'),
            'from': _('{} von {}'),
            # backward compatibility
            'member': lambda: Config.vocabulary('account'),
            'member_pl': lambda: Config.vocabulary('account_pl'),
            # additional vocabulary to adjust for gender and cases
            'this_account': v_format(_('dieses {account}'), 'account'),
            'the_assignment_acc': v_format(_('den {assignment}'), 'assignment'),
            'not_a_member_type': v_format(_('kein {member_type}'), 'member_type'),
            'your_membership_acc': v_format(_('deine {membership}'), 'membership'),
            'this_share': v_format(_('dieser {share}'), 'share'),
            'this_share_acc': v_format(_('diesen {share}'), 'share'),
            'no_share': v_format(_('kein {share}'), 'share'),
            'the_depot_acc': v_format(_('das {depot}'), 'depot'),
            'the_depot_dat': v_format(_('dem {depot}'), 'depot'),
            'to_the_depot': v_format(_('zum {depot}'), 'depot'),
            'your_depot': v_format(_('dein {depot}'), 'depot'),
            'the_subscription': v_format(_('das {subscription}'), 'subscription'),
            'the_subscription_acc': lambda: Config.vocabulary('the_subscription'),
            'no_subscription_acc': v_format(_('kein {subscription}'), 'subscription'),
            'this_subscription_acc': v_format(_('dieses {subscription}'), 'subscription'),
            'this_subscription_dat': v_format(_('diesem {subscription}'), 'subscription'),
            'your_subscription_acc': v_format(_('dein {subscription}'), 'subscription'),
            'with_active_subscription': v_format(_('mit aktivem {subscription}'), 'subscription'),

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
    organisation_website = _get_setting_with_key(
        'ORGANISATION_WEBSITE',
        {
            'name': lambda: Config.server_url(),
            'url': lambda: 'http://' + Config.server_url()
        }
    )
    organisation_bank_connection = _get_setting(
        'ORGANISATION_BANK_CONNECTION',
        {
            'PC': '01-123-5',
            'IBAN': 'CH 00 12345 67890 12345 67890 10',
            'BIC': 'BIC1234500',
            'NAME': 'Juntagrico Bank',
        }
    )
    share_price = _get_setting('SHARE_PRICE', 250)

    @classmethod
    def share_price_display(cls):
        if not hasattr(cls, '_share_price_display'):
            from juntagrico.templatetags.juntagrico.common import price
            cls._share_price_display = price(cls.share_price())
        return cls._share_price_display

    business_regulations = _get_setting('BUSINESS_REGULATIONS')
    bylaws = _get_setting('BYLAWS')
    gdpr_info = _get_setting('GDPR_INFO')
    faq_doc = _get_setting('FAQ_DOC')
    extra_sub_info = _get_setting('EXTRA_SUB_INFO')
    activity_area_info = _get_setting('ACTIVITY_AREA_INFO')
    enable_shares = _get_setting('ENABLE_SHARES', True)
    membership = _get_setting_with_key(
        'MEMBERSHIP',
        {
            'enable': True,
            'required_shares': 1,
            'required_on_signup': True,
            'fee': 0,
        }
    )

    @classmethod
    def enable_membership(cls):
        return cls.membership('enable')

    required_shares = _get_setting('REQUIRED_SHARES', 1)
    enable_registration = _get_setting('ENABLE_REGISTRATION', True)
    require_subscription = _get_setting('REQUIRE_SUBSCRIPTION', False)
    signup_manager = _get_setting('SIGNUP_MANAGER', 'juntagrico.util.sessions.SignupManager')
    enable_external_signup = _get_setting('ENABLE_EXTERNAL_SIGNUP', False)
    enforce_mail_confirmation = _get_setting('ENFORCE_MAIL_CONFIRMATION', True)

    base_fee = _get_setting('BASE_FEE')
    raw_currency = _get_setting('CURRENCY', 'CHF {}')

    @classmethod
    def currency(cls):
        if not hasattr(cls, '_currency'):
            sys.stderr.write('Config.currency is deprecated since 2.1. Use currency_format instead.\n')
            raw_currency = cls.raw_currency()
            cls._currency = raw_currency.strip(' {}')
        return cls._currency

    @classmethod
    def currency_format(cls):
        if not hasattr(cls, '_currency_format'):
            raw_currency = cls.raw_currency()
            cls._currency_format = raw_currency if '{}' in raw_currency else (str(raw_currency) + ' {}').strip()
        return cls._currency_format

    assignment_unit = _get_setting('ASSIGNMENT_UNIT', 'ENTITY')
    allow_job_unsubscribe = _get_setting('ALLOW_JOB_UNSUBSCRIBE', False)
    jobs_frontpage = _get_setting_with_key(
        'JOBS_FRONTPAGE',
        {
            'days': 14,
            'min': 3,
            'max': 10,
            'promoted_types': [],
            'promoted_count': 2
        }
    )
    first_job_info = _get_setting('FIRST_JOB_INFO', ['overall'])

    @staticmethod
    def depot_lists(default_names=None, context=None):
        default_names = default_names or {}
        values = getattr(settings, 'DEPOT_LISTS', defaults.DEPOT_LISTS)
        # normalize
        for file_name, conf in values.items():
            if not isinstance(conf, dict):
                conf = dict(template=conf)
            if context is not None:
                if callable(conf.get('extra_context')):
                    conf['extra_context'] = conf['extra_context'](context)
                elif 'extra_context' not in conf:
                    conf['extra_context'] = {}
            if 'name' not in conf:
                conf['name'] = default_names.get(file_name, file_name)
            yield dict(file_name=file_name, **conf)

    depot_list_generation_days = _get_setting('DEPOT_LIST_GENERATION_DAYS', [0, 1, 2, 3, 4, 5, 6])
    default_depot_list_generators = _get_setting('DEFAULT_DEPOTLIST_GENERATORS', ['juntagrico.util.depot_list.default_depot_list_generation'])
    business_year_start = _get_setting('BUSINESS_YEAR_START', {'day': 1, 'month': 1})
    business_year_cancelation_month = _get_setting('BUSINESS_YEAR_CANCELATION_MONTH', 12)
    membership_end_month = _get_setting('MEMBERSHIP_END_MONTH', 6)
    membership_end_notice_period = _get_setting('MEMBERSHIP_END_NOTICE_PERIOD', 0)
    cookie_consent = _get_setting_with_key(
        'COOKIE_CONSENT',
        {
            'text': lambda: _('{} verwendet folgende Cookies: session, csfr, cookieconsent.').format(
                Site.objects.get_current().name),
            'confirm_text': _('einverstanden'),
            'link_text': _('Hier findest du mehr zum Thema'),
            'url': '/my/cookies'
        }
    )
    sub_overview_format = _get_setting_with_key(
        'SUB_OVERVIEW_FORMAT',
        {
            'delimiter': '|',
            'format': '{category}:{bundle}:{type}={amount}',
            'part_format': '{bundle}'
        }
    )

    # url and email settings
    info_email = _get_setting('INFO_EMAIL', 'info@juntagrico.juntagrico')
    contacts = _get_setting_with_key(
        'CONTACTS',
        {
            'general': lambda: Config.info_email(),
            'for_members': lambda: Config.contacts('general'),
            'for_subscriptions': lambda: Config.contacts('general'),
            'for_shares': lambda: Config.contacts('general'),
            'technical': lambda: Config.contacts('general'),
        }
    )
    url_protocol = _get_setting('URL_PROTOCOL', 'https://')
    server_url = _get_setting('SERVER_URL', 'www.juntagrico.juntagrico')
    batch_mailer = _get_setting_with_key(
        'BATCH_MAILER',
        {
            'batch_size': 39,
            'wait_time': 65
        })
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
    favicon = _get_setting('FAVICON', fallback_static('juntagrico/img/favicon.ico'))
    bootstrap = _get_setting('BOOTSTRAP', fallback_static('juntagrico/external/bootstrap/css/bootstrap.min.css'))
    styles = _get_setting_with_key('STYLES', {'template': '', 'static': []})
    scripts = _get_setting_with_key('SCRIPTS', {'template': '', 'static': []})
    images = _get_setting_with_key(
        'IMAGES',
        {
            'status_100': fallback_static('juntagrico/img/status_100.png'),
            'status_75': fallback_static('juntagrico/img/status_75.png'),
            'status_50': fallback_static('juntagrico/img/status_50.png'),
            'status_25': fallback_static('juntagrico/img/status_25.png'),
            'status_0': fallback_static('juntagrico/img/status_0.png'),
            'single_full': fallback_static('juntagrico/img/single_full.png'),
            'single_empty': fallback_static('juntagrico/img/single_empty.png'),
            'single_core': fallback_static('juntagrico/img/single_core.png'),
            'core': fallback_static('juntagrico/img/core.png')
        }
    )

    @classmethod
    def using_richtext(cls):
        try:
            return (
                'djrichtextfield' in settings.INSTALLED_APPS
                and isinstance(settings.DJRICHTEXTFIELD_CONFIG['profiles']['juntagrico.admin'], dict)
            )
        except (AttributeError, KeyError):
            return False

    @classmethod
    def notifications(cls, name):
        default_notifications = [
            'job_subscription_changed',
            'job_unsubscribed',
            'membership_activated',
            'membership_deactivated',
        ] + [
            # notify by default on first jobs as they are shown by FIRST_JOB_INFO setting
            FIRST_JOB_NOTIFICATION_MAP[first_job_info] for first_job_info in cls.first_job_info()
        ]
        enabled_notifications = getattr(settings, 'ENABLE_NOTIFICATIONS', []) + default_notifications
        disabled_notifications = getattr(settings, 'DISABLE_NOTIFICATIONS', [])
        return name in enabled_notifications and name not in disabled_notifications

    @classmethod
    def documents(cls, tag, in_sentence=False):
        documents = getattr(settings, 'DOCUMENTS', [])

        # get values from dedicated settings
        if business_regulations := cls.business_regulations().strip():
            documents.append(((gettext('Betriebsreglement'), gettext('das Betriebsreglement')), business_regulations, 'account-signup-accept subscription'))
        if bylaws := cls.bylaws().strip():
            documents.append(((gettext('Statuten'), gettext('die Statuten')), bylaws, 'membership-signup-accept account subscription'))
        if gdpr_info := cls.gdpr_info().strip():
            documents.append(((gettext('DSGVO Infos'), gettext('die DSGVO Infos')), gdpr_info, 'account-signup-accept subscription'))
        if faq_doc := cls.faq_doc().strip():
            documents.append((gettext('Häufig gestellte Fragen'), faq_doc, 'account'))
        if extra_sub_info := cls.extra_sub_info().strip():
            documents.append((gettext('Infos zu den Zusatz-Abos'), extra_sub_info, 'extrasub'))
        if activity_area_info := cls.activity_area_info().strip():
            documents.append((gettext('Infoblatt'), activity_area_info, 'activityarea'))

        normalized_documents = []
        for names, link, tags in documents:
            if tag in tags:
                if isinstance(names, (list, tuple)):
                    name = names[int(in_sentence)]
                else:
                    name = names
                normalized_documents.append((name, link))
        return normalized_documents

    # demo settings
    demouser = _get_setting('DEMO_USER')
    demopwd = _get_setting('DEMO_PWD')
