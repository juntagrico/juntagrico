from django.http import HttpResponse, HttpResponseServerError
from django.contrib.auth.decorators import login_required

from django.template.loader import get_template
from django.template import Context

from xhtml2pdf import pisa



def render_to_pdf(request, template_name, renderdict):
    """
    Take a string of rendered html and pack it into a pdf.
    """
    rendered_html = get_template(template_name).render(Context(renderdict))

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="test.pdf"'

    success = pisa.CreatePDF(rendered_html, dest=response)

    if not success:
        return HttpResponseServerError()
    return response

