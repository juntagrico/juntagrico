import hashlib

from django.template.defaultfilters import slugify


def make_username(firstname, lastname, email):
    firstname = slugify(firstname)[:10]
    lastname = slugify(lastname)[:10]
    email = hashlib.sha1(email.encode('utf-8')).hexdigest()
    return ('%s_%s_%s' % (firstname, lastname, email))[:30]
