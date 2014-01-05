from django.http import HttpResponse, HttpResponseServerError

from django.template.loader import get_template
from django.template import Context

from xhtml2pdf import pisa

from django.contrib.auth.models import User


class AuthenticateWithEmail(object):
    def authenticate(self, username=None, password=None):
        from models import Loco
        try:
            user = Loco.objects.get(**{'email': username}).user
            if user.check_password(password):
                return user
        except Loco.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def render_to_pdf(request, template_name, renderdict, filename):
    """
    Take a string of rendered html and pack it into a pdf.
    """
    rendered_html = get_template(template_name).render(Context(renderdict))

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

    success = pisa.CreatePDF(rendered_html, dest=response)

    if not success:
        return HttpResponseServerError()
    return response


weekday_choices = ((1, "Montag"),
                   (2, "Dienstag"),
                   (3, "Mittwoch"),
                   (4, "Donnerstag"),
                   (5, "Freitag"),
                   (6, "Samstag"),
                   (7, "Sonntag"))

weekdays = dict(weekday_choices)

