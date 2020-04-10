from io import BytesIO

from django.db import models
from django.http import HttpResponse
from xlsxwriter import Workbook


def generate_excel(fields, data, download_name=None):
    """
    Generate an excel document and write it to a http response.
    Returns the response object.

    fields may be a list of field-names or a list of tuples containing
    field-name and field-label.

    data may be a list of objects or dictionaries or a model query-set.
    In the case of query-set the field labels are determined from the
    model metadata.
    """
    if isinstance(data, models.Model):
        data_name = data.verbose_name
    else:
        data_name = 'Report'
    download_name = download_name or data_name

    output = BytesIO()
    workbook = Workbook(output)
    writer = ExcelWriter(fields, workbook)
    writer.write_data(data)
    workbook.close()
    t = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(content_type=t)
    disposition = 'attachment; filename=%s.xlsx' % download_name
    response['Content-Disposition'] = disposition
    response.write(output.getvalue())

    return response


class ExcelWriter(object):
    """
    Helper class for writing data to an excel workbook.

    fields may be a list of field-names or a list of tuples containing
    field-name and field-label.

    data may be a list of objects or dictionaries or a model query-set.
    In the case of query-set the field labels are determined from the
    model metadata.

    Excel field-types are determined based on the data written.
    Column-widths in excel are set automatically based on
    the column (field) labels.
    """

    def __init__(self, fields, workbook):
        self.fields = fields
        self.workbook = workbook
        self.fieldtypes = [None for i in range(len(self.fields))]

    def write_data(self, data):
        """
        main method of ExcelWriter object, must be called
        when using ExcelWriter.
        """
        if isinstance(data, models.base.ModelBase):
            list_data = data.objects.all()
            self.model = data
        else:
            list_data = data
            self.model = None

        # create a worksheet
        self.worksheet = self.workbook.add_worksheet()
        self.write_header()

        # write data rows
        row = 1
        for item in list_data:
            col = 0
            for fielddef in self.fields:
                if isinstance(fielddef, str):
                    fieldname = fielddef
                else:
                    fieldname, label = fielddef
                value = self.get_value(item, fieldname)
                self.worksheet.write(row, col, value)

                # record field-type from value
                if (not self.fieldtypes[col]) and value:
                    self.fieldtypes[col] = type(value).__name__

                col += 1
            row += 1

        self.format_columns()

    def write_header(self):
        row = 0
        col = 0
        # assign format
        header_format = self.workbook.add_format({'bold': True})
        self.worksheet.set_row(0, None, header_format)

        # write header labels
        for label in self.get_header_labels():
            self.worksheet.write_string(row, col, label)
            col += 1

    def format_columns(self):
        min_width = 8

        # define numeric formats
        curr_format = self.workbook.add_format({'num_format': '#0.00'})
        date_format = self.workbook.add_format({'num_format': 'dd/mm/yy'})

        for i, label in enumerate(self.get_header_labels()):
            fieldtype = self.fieldtypes[i]

            fmt = None
            if fieldtype == 'date':
                fmt = date_format
            if fieldtype == 'float':
                fmt = curr_format
            width = max(min_width, len(label) * 1.2)
            self.worksheet.set_column(i, i, width, fmt)

    def get_header_labels(self):
        result = []
        for fielddef in self.fields:
            if isinstance(fielddef, str):
                if self.model:
                    label = self.get_label_from_model(self.model, fielddef)
                else:
                    label = fielddef
            else:
                fieldname, label = fielddef
            result.append(label)

        return result

    def get_value(self, item, field_expression):
        # on dictionaries, expression is just the key
        if isinstance(item, dict):
            return item.get(field_expression, "")

        # on model items we support multi-term expressions
        parts = field_expression.split('.')
        count = 1
        fieldvalue = getattr(item, parts[0])
        while count < len(parts) and fieldvalue is not None:
            fieldvalue = getattr(fieldvalue, parts[count])
            count += 1
        return fieldvalue

    def get_label_from_model(self, model, field_expression):
        parts = field_expression.split('.')
        count = 1
        dbfield = model._meta.get_field(parts[0])
        while count < len(parts):
            dbfield = dbfield.related_model._meta.get_field(parts[count])
            count += 1
        return dbfield.verbose_name
