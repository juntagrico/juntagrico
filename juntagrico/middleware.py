from fnmatch import fnmatchcase

from django.shortcuts import redirect
from django.urls import Resolver404, resolve, ResolverMatch

from juntagrico.config import Config


def view_match(match: ResolverMatch | None, allowed: set[str]) -> bool:
    """ checks if a resolver_match matches any pattern in allowed.
    the patterns may contain namespaces (optional) and url names with wildcards
    E.g.
    allowed={'home', 'profile-*', 'oauth:*', 'billing:bill'}
    """
    if not match:
        return False

    view_name = match.view_name or ""
    url_name = match.url_name or ""

    return any(
        fnmatchcase(view_name, rule) if ":" in rule
        else fnmatchcase(url_name, rule)
        for rule in allowed
    )


class RequirePasswordChangeMiddleware:
    password_view_name = 'password'
    session_key_name = 'must_change_password'
    allowed_url_names = {password_view_name, 'logout', 'js-i18n', 'impersonate-stop'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.session.get(
            self.session_key_name
        ):
            try:
                match = request.resolver_match or resolve(
                    request.path_info,
                    urlconf=getattr(request, 'urlconf', None),
                )
            except Resolver404:
                match = None

            if not view_match(match, self.get_allowed_url_names()):
                return redirect(self.password_view_name)

        return self.get_response(request)

    def get_allowed_url_names(self):
        return self.allowed_url_names | set(Config.always_allowed_url_names())
