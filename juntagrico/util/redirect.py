from urllib.parse import urlsplit

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, resolve, Resolver404


def safe_redirect(url):
    """Return a redirect to a resolvable local path, or None if invalid."""
    if not url:
        return None

    parts = urlsplit(url)
    path = parts.path
    if not path.startswith('/') or path.startswith('//') or '\\' in path:
        return None

    try:
        resolve(path)
    except (ValueError, Resolver404):
        return None

    query = parts.query
    fragment = parts.fragment
    destination = path + (f"?{query}" if query else "") + (f"#{fragment}" if fragment else "")
    return HttpResponseRedirect(destination)


def return_to_previous_location(request):
    referer = request.META.get("HTTP_REFERER", "")
    return safe_redirect(referer) or redirect(reverse("home"))
