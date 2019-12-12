from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseServerError
from django.template.loader import get_template
from xhtml2pdf import pisa


def render_to_pdf_http(template_name, renderdict, filename):
    '''
    Take a string of rendered html and pack it
    into a pdfand return it thtough http
    '''
    rendered_html = get_template(template_name).render(renderdict)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = "attachment; filename='" + filename + "'"

    success = pisa.CreatePDF(rendered_html, dest=response)

    if not success:
        return HttpResponseServerError()
    return response


def return_pdf_http(filename):
    if default_storage.exists(filename):
        with default_storage.open(filename) as pdf_file:
            content = pdf_file.read()
        content_disposition = "attachment; filename=" + filename
        response = HttpResponse(content, content_type='application/pdf')
        response['Content-Disposition'] = content_disposition
        return response
    else:
        return HttpResponseServerError()


def render_to_pdf_storage(template_name, renderdict, filename):
    '''
    Take a string of rendered html and pack it into a pdfand save it
    '''
    if default_storage.exists(filename):
        default_storage.delete(filename)
    rendered_html = get_template(template_name).render(renderdict)
    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(str(rendered_html).encode('utf-8')), dest=pdf)
    default_storage.save(filename, ContentFile(pdf.getvalue()))
