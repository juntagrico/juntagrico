
from django.contrib.auth.models import Group
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import ValidationError
from django.test import override_settings, RequestFactory
from django.urls import reverse, resolve

from juntagrico.defaults import allow_group, user_queryset, password_validators
from juntagrico.middleware import view_match, RequirePasswordChangeMiddleware
from juntagrico.util.redirect import safe_redirect
from . import JuntagricoTestCaseWithShares


fake_response = type('Response', (), {'status_code': 200})()

DOC_DEFAULT_VALIDATORS = password_validators
DOC_EXAMPLE_VALIDATORS = [
    {
        'NAME': 'juntagrico.password_validation.PrivilegedOnlyPasswordValidator',
        'OPTIONS': {
            'validators': [
                {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
                 'OPTIONS': {'min_length': 16}},
                {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
            ],
        }
    },
    {
        'NAME': 'juntagrico.password_validation.GroupOnlyPasswordValidator',
        'OPTIONS': {
            'validators': password_validators,
            'group_name': 'my_group',
        }
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 14}},
]


@override_settings(
    AUTH_PASSWORD_VALIDATORS=[
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {'min_length': 12},
        },
    ]
)
class PasswordValidationTests(JuntagricoTestCaseWithShares):
    """Tests for password validation flow in login and password change views."""

    def test_login_with_weak_password_sets_session_flag(self):
        """When a user logs in with a weak password, the session should be flagged
        for password change (auth.py lines 77-82)."""
        # Set a weak password and confirm the member
        self.member.user.set_password('short')
        self.member.user.save()
        self.member.confirmed = True
        self.member.save()
        # Login with the weak password
        response = self.client.post(reverse('login'), {
            'username': self.member.email,
            'password': 'short',
        })
        # User should be logged in (redirect), and session flag set
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('must_change_password'))

    def test_password_change_clears_session_flag(self):
        """When a user successfully changes their password, the must_change_password
        session flag should be cleared (authentication.py lines 17-19)."""
        self.member.user.set_password('OldPass123!')
        self.member.user.save()
        self.client.force_login(self.member.user)
        self.client.session['must_change_password'] = True
        self.client.session.save()
        # Submit a valid password change
        response = self.client.post(reverse('password'), {
            'old_password': 'OldPass123!',
            'new_password1': 'SecurePass123!abc',
            'new_password2': 'SecurePass123!abc',
        })
        self.assertEqual(response.status_code, 302)
        # Session flag should be cleared - check via a new request
        response = self.client.get(reverse('password'))
        self.client.session.load()
        self.assertIsNone(self.client.session.get('must_change_password'))

    def test_password_change_page_with_must_change_flag(self):
        """The password page should show the warning when must_change_password is set
        (password.html lines 17-19)."""
        self.client.force_login(self.member.user)
        sid = self.client.cookies['sessionid'].value
        store = SessionStore(session_key=sid)
        store.load()
        store['must_change_password'] = True
        store.save()
        response = self.client.get(reverse('password'))
        self.assertContains(response, 'Setze ein neues sicheres Passwort.')

    def test_password_changed_view(self):
        """The password_changed view renders the success page (views/__init__.py line 270)."""
        self.client.force_login(self.member.user)
        response = self.client.get(reverse('password_change_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('success', False))


class MiddlewareTests(JuntagricoTestCaseWithShares):
    """Tests for RequirePasswordChangeMiddleware."""

    def _make_request(self, url_name):
        """Build a request with must_change_password set for middleware testing."""
        request = RequestFactory().get(reverse(url_name))
        request.user = self.member.user
        session = SessionStore()
        session['must_change_password'] = True
        session.create()
        request.session = session
        request.resolver_match = resolve(reverse(url_name))
        return request

    def test_middleware_allows_password_url(self):
        """Password view is in the allowed list, so it passes through without redirect."""
        request = self._make_request('password')
        middleware = RequirePasswordChangeMiddleware(lambda r: fake_response)
        response = middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_middleware_redirects_for_non_allowed_url(self):
        """home is not in the allowed list, so it redirects to password."""
        request = self._make_request('home')
        middleware = RequirePasswordChangeMiddleware(lambda r: fake_response)
        response = middleware(request)
        self.assertEqual(response.status_code, 302)

    def test_middleware_no_redirect_when_flag_not_set(self):
        """Middleware should not redirect when must_change_password is not set."""
        self.client.force_login(self.member.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_view_match_with_none(self):
        """view_match should return False when match is None (middleware.py lines 15-16)."""
        self.assertFalse(view_match(None, {'home', 'password'}))

    def test_view_match_with_wildcard(self):
        """view_match should support wildcard patterns (fnmatch)."""
        match = resolve(reverse('manage-shares'))
        self.assertTrue(view_match(match, {'manage*'}))
        self.assertFalse(view_match(match, {'manage'}))

    @override_settings(ALWAYS_ALLOWED_URLNAMES=['home'])
    def test_middleware_with_custom_allowed_names(self):
        """When home is added to allowed names, it passes through without redirect."""
        request = self._make_request('home')
        middleware = RequirePasswordChangeMiddleware(lambda r: fake_response)
        allowed = middleware.get_allowed_url_names()
        self.assertIn('home', allowed)
        response = middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_middleware_resolver404_path(self):
        """When a path cannot be resolved, middleware redirects to password page."""
        request = RequestFactory().get('/nonexistent-path/')
        request.user = self.member.user
        session = SessionStore()
        session['must_change_password'] = True
        session.create()
        request.session = session
        middleware = RequirePasswordChangeMiddleware(lambda r: fake_response)
        response = middleware(request)
        self.assertEqual(response.status_code, 302)


class RedirectSafetyTests(JuntagricoTestCaseWithShares):
    """Tests for safe_redirect utility."""

    def test_safe_redirect_with_backslash(self):
        """safe_redirect should reject paths containing backslashes (redirect.py line 16)."""
        result = safe_redirect('http://example.com/path\\with\\backslash')
        self.assertIsNone(result)

    def test_safe_redirect_with_invalid_path(self):
        """safe_redirect should reject paths not starting with /."""
        result = safe_redirect('http://example.com')
        self.assertIsNone(result)

    def test_safe_redirect_with_double_slash(self):
        """safe_redirect should reject paths starting with //."""
        result = safe_redirect('http://example.com//etc/passwd')
        self.assertIsNone(result)

    def test_safe_redirect_resolver404(self):
        """safe_redirect should return None for unresolvable paths (redirect.py lines 20-21)."""
        result = safe_redirect('http://example.com/nonexistent-page/')
        self.assertIsNone(result)

    def test_safe_redirect_valid_path(self):
        """safe_redirect should return HttpResponseRedirect for valid paths."""
        result = safe_redirect('http://example.com/')
        self.assertIsNotNone(result)
        self.assertEqual(result.url, '/')

    def test_safe_redirect_none(self):
        """safe_redirect should return None for empty input."""
        self.assertIsNone(safe_redirect(''))
        self.assertIsNone(safe_redirect(None))


# don't install impersonate
NO_INSTALLED_APPS = override_settings(INSTALLED_APPS=[
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'juntagrico.apps.JuntagricoAdminConfig',
    'juntagrico',
    'crispy_forms',
    'crispy_bootstrap4',
    'adminsortable2',
    'django_select2',
    'polymorphic',
    'import_export',
    'djrichtextfield',
])


class ImpersonationTests(JuntagricoTestCaseWithShares):
    """Tests for impersonation-related code."""

    @NO_INSTALLED_APPS
    def test_allow_impersonate_without_app(self):
        """Config.allow_impersonate should return False when impersonate is not installed
        (config.py line 267)."""
        from juntagrico.config import Config
        request = type('Request', (), {'user': self.admin.user})()
        self.assertFalse(Config.allow_impersonate(request))

    @NO_INSTALLED_APPS
    def test_member_admin_pop_impersonate_action(self):
        """MemberAdmin.get_actions should pop impersonate_job when allow_impersonate returns False
        (member_admin.py line 65)."""
        from juntagrico.admins.member_admin import MemberAdmin
        from django.contrib.auth.models import User
        from django.contrib.admin import AdminSite
        admin = MemberAdmin(User, AdminSite())
        request = RequestFactory().get('/')
        request.user = self.admin.user
        actions = admin.get_actions(request)
        self.assertNotIn('impersonate_job', actions)

    def test_allow_group_helper(self):
        """Test the allow_group helper function (defaults.py lines 99-101)."""
        # Create a group
        group = Group.objects.create(name='test_impersonators')
        check = allow_group('test_impersonators')
        # Member not in group
        request = type('Request', (), {'user': self.member.user})()
        self.assertFalse(check(request))
        # Member in group
        self.member.user.groups.add(group)
        self.assertTrue(check(request))
        self.member.user.groups.remove(group)
        group.delete()

    def test_user_queryset_helper(self):
        """Test the user_queryset helper function (defaults.py lines 113-116)."""
        check = user_queryset(unless_superuser=True, is_staff=False)
        # Create a mock request with a superuser
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        superuser = User.objects.create_user(
            username='superuser_test',
            password='test',
            is_superuser=True,
        )
        rf = RequestFactory()
        request = rf.get('/')
        request.user = superuser
        # For superuser, should return all users
        qs = check(request)
        self.assertEqual(qs.count(), User.objects.count())
        superuser.delete()

    def test_user_queryset_non_superuser(self):
        """Test user_queryset with a non-superuser (defaults.py lines 113-116)."""
        check = user_queryset(unless_superuser=True, is_staff=False)
        from django.test import RequestFactory
        rf = RequestFactory()
        request = rf.get('/')
        # member2 is not a staff user
        request.user = self.member2.user
        qs = check(request)
        # Non-staff users should be in the queryset
        self.assertTrue(qs.filter(pk=self.member2.user.pk).exists())


class MailTemplateAdminTests(JuntagricoTestCaseWithShares):
    """Tests for MailTemplateAdmin with unlock_mailtemplates setting."""

    @override_settings(UNLOCK_MAILTEMPLATES=True)
    def test_mail_template_add_permission_unlocked(self):
        """When UNLOCK_MAILTEMPLATES is True, add permission should be granted
        (mail_template_admin.py line 11)."""
        from juntagrico.admins.mail_template_admin import MailTemplateAdmin
        from juntagrico.entity.mailing import MailTemplate
        admin = MailTemplateAdmin(MailTemplate, None)
        request = type('Request', (), {'user': self.admin.user})()
        self.assertTrue(admin.has_add_permission(request))

    @override_settings(UNLOCK_MAILTEMPLATES=True)
    def test_mail_template_readonly_fields_unlocked(self):
        """When UNLOCK_MAILTEMPLATES is True, readonly fields should be inherited
        (mail_template_admin.py lines 15-17)."""
        from juntagrico.admins.mail_template_admin import MailTemplateAdmin
        from juntagrico.entity.mailing import MailTemplate
        admin = MailTemplateAdmin(MailTemplate, None)
        request = type('Request', (), {'user': self.admin.user})()
        readonly = admin.get_readonly_fields(request, None)
        # When unlocked, should return the base readonly fields (empty list)
        self.assertNotIn('template', readonly)
        self.assertNotIn('code', readonly)

    def test_mail_template_add_permission_locked(self):
        """When UNLOCK_MAILTEMPLATES is False (default), add permission should be denied."""
        from juntagrico.admins.mail_template_admin import MailTemplateAdmin
        from juntagrico.entity.mailing import MailTemplate
        admin = MailTemplateAdmin(MailTemplate, None)
        request = type('Request', (), {'user': self.admin.user})()
        self.assertFalse(admin.has_add_permission(request))

    def test_mail_template_readonly_fields_locked(self):
        """When UNLOCK_MAILTEMPLATES is False, template and code should be readonly."""
        from juntagrico.admins.mail_template_admin import MailTemplateAdmin
        from juntagrico.entity.mailing import MailTemplate
        admin = MailTemplateAdmin(MailTemplate, None)
        request = type('Request', (), {'user': self.admin.user})()
        readonly = admin.get_readonly_fields(request, None)
        self.assertIn('template', readonly)
        self.assertIn('code', readonly)


@override_settings(AUTH_PASSWORD_VALIDATORS=DOC_DEFAULT_VALIDATORS)
class DocDefaultPasswordValidatorsTests(JuntagricoTestCaseWithShares):
    """Tests for the default password validators example from docs/intro/deployment.rst."""

    def test_default_validators_reject_short_password(self):
        """Reject passwords shorter than 12 characters."""
        from django.contrib.auth.password_validation import validate_password
        with self.assertRaises(ValidationError):
            validate_password('Short1!', self.member.user)

    def test_default_validators_accept_strong_password(self):
        """Accept a strong password of 12+ characters."""
        from django.contrib.auth.password_validation import validate_password
        validate_password('MySecurePass123!', self.member.user)

    def test_default_validators_reject_email_as_password(self):
        """Reject the user's email as password."""
        from django.contrib.auth.password_validation import validate_password
        with self.assertRaises(ValidationError):
            validate_password(self.member.email, self.member.user)


@override_settings(AUTH_PASSWORD_VALIDATORS=DOC_EXAMPLE_VALIDATORS)
class DocExamplePasswordValidationTests(JuntagricoTestCaseWithShares):
    """Tests for the role-based password validation example from docs/intro/deployment.rst."""

    def test_privileged_user_requires_strong_password(self):
        """Staff user should require min 16 chars."""
        from django.contrib.auth.password_validation import validate_password
        self.admin.user.is_staff = True
        self.admin.user.save()
        with self.assertRaises(ValidationError):
            validate_password('Exactly15chars!', self.admin.user)

    def test_non_privileged_user_uses_fallback(self):
        """Regular member should use fallback min 14 chars."""
        from django.contrib.auth.password_validation import validate_password
        validate_password('MySecurePassword123!', self.member.user)
        with self.assertRaises(ValidationError):
            validate_password('Short1234!', self.member.user)

    def test_group_member_uses_group_validators(self):
        """User in 'my_group' should be subject to group validators."""
        from django.contrib.auth.password_validation import validate_password
        group = Group.objects.create(name='my_group')
        self.member.user.groups.add(group)
        validate_password('MySecurePassword123!', self.member.user)
        with self.assertRaises(ValidationError):
            validate_password(self.member.email, self.member.user)
        self.member.user.groups.remove(group)
        group.delete()

    def test_coordinator_requires_strong_password(self):
        """Coordinator should require min 16 chars."""
        from django.contrib.auth.password_validation import validate_password
        from juntagrico.entity.jobs import ActivityArea
        area = ActivityArea.objects.create(name='Test Area')
        self.member.coordinated_areas.add(area)
        with self.assertRaises(ValidationError):
            validate_password('Exactly15chars!', self.member.user)
        validate_password('LongEnoughPassword123!', self.member.user)
        self.member.coordinated_areas.remove(area)
        area.delete()
