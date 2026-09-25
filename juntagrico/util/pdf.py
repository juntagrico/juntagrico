from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, storages, InvalidStorageError
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.template.loader import get_template
from django.utils.functional import LazyObject
from xhtml2pdf import pisa


class InternalStorage(LazyObject):
    def _setup(self):
        try:
            self._wrapped = storages['internal']
        except InvalidStorageError:
            self._wrapped = FileSystemStorage(location='internal_files')


internal_storage = InternalStorage()


def render_to_pdf_http(template_name, renderdict, filename):
    '''
    Take a string of rendered html and pack it
    into a pdf and return it through http
    '''
    rendered_html = get_template(template_name).render(renderdict)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = "attachment; filename=\"" + filename + "\""

    success = pisa.CreatePDF(rendered_html, dest=response)

    if not success:
        return HttpResponseServerError()
    return response


def return_pdf_http(filename):
    if not internal_storage.exists(filename):
        raise Http404
    with internal_storage.open(filename) as pdf_file:
        content = pdf_file.read()
    content_disposition = "attachment; filename=" + filename
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = content_disposition
    return response


def render_to_pdf_storage(template_name, context, filename):
    '''
    Take a string of rendered html and pack it into a pdf and save it
    '''
    if internal_storage.exists(filename):
        internal_storage.delete(filename)
    rendered_html = get_template(template_name).render(context)
    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(str(rendered_html).encode('utf-8')), dest=pdf)
    internal_storage.save(filename, ContentFile(pdf.getvalue()))
