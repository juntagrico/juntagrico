from django.shortcuts import redirect
from django.urls import Resolver404, resolve


class RequirePasswordChangeMiddleware:
    allowed_url_names = {"password", "logout"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and request.session.get("must_change_password")
        ):
            try:
                match = request.resolver_match or resolve(
                    request.path_info,
                    urlconf=getattr(request, 'urlconf', None),
                )
            except Resolver404:
                match = None

            if not match or match.url_name not in self.allowed_url_names:
                return redirect("password")

        return self.get_response(request)
