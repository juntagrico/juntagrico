from io import StringIO, BytesIO

import xlsxwriter
from django.http import HttpResponse

'''
    Generates excell for a defined set of fields and a model
'''

def generate_excell_from_model(fields, model_instance):
    parsed_fields={}
    for field in fields:
        parts = field.split('.')
        count = 1
        dbfield = model_instance._meta.get_field(parts[0])
        while count < len(parts):
            dbfield = dbfield.related_model._meta.get_field(parts[count])
            count += 1
        parsed_fields.update({field: dbfield.verbose_name})

    instances = model_instance.objects.all()
    return generate_excell(parsed_fields, instances)

def generate_excell_load_fields(fields, model_instance,instances):
    for field in fields:
        if fields[field]=='':
            parts = field.split('.')
            count = 1
            dbfield = model_instance._meta.get_field(parts[0])
            while count < len(parts):
                dbfield = dbfield.related_model._meta.get_field(parts[count])
                count += 1
            fields[field] = dbfield.verbose_name

    return generate_excell(fields, instances)
    
def generate_excell(fields, instances):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet_s = workbook.add_worksheet('export')

    col = 0
    for field in fields:
        worksheet_s.write(0, col, fields[field])
        col += 1

    row = 1
    for instance in instances:
        col = 0
        for field in fields:
            parts = field.split('.')
            count = 1
            fieldvalue = getattr(instance, parts[0])
            while count < len(parts) and fieldvalue is not None:
                fieldvalue = getattr(fieldvalue, parts[count])
                count += 1
            if fieldvalue is not None:
                worksheet_s.write(row, col, str(fieldvalue))
            col += 1
        row += 1

    workbook.close()
    xlsx_data = output.getvalue()
    response.write(xlsx_data)
    return response
