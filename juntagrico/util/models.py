'''
    Copys the user defined attributes of a model into another model. It will only copy the fields with are present in both
'''


def attribute_copy(source, target):
    for field in target._meta.fields:
        if field.auto_created is False and field.editable is True and field.attname in source.__dict__ and field.attname in target.__dict__:
            target.__dict__[field.attname] = source.__dict__[field.attname]
