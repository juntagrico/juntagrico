import random
import string

from django.template.defaultfilters import slugify


def make_username(firstname, lastname):
    firstname = slugify(firstname)[:10]
    lastname = slugify(lastname)[:10]
    seed = slugify(''.join(random.choices(string.ascii_uppercase + string.digits, k=10)))
    return ('%s_%s_%s' % (firstname, lastname, seed))[:30]
