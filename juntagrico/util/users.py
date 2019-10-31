import hashlib

from django.contrib.auth.models import Permission, User
from django.db.models import Q
from django.template.defaultfilters import slugify


def make_username(firstname, lastname, email):
    firstname = slugify(firstname)[:10]
    lastname = slugify(lastname)[:10]
    email = hashlib.sha1(email.encode('utf-8')).hexdigest()
    return ('%s_%s_%s' % (firstname, lastname, email))[:30]


def get_users_by_permission(permission_codename):
    perm = Permission.objects.get(codename=permission_codename)
    return User.objects.filter(Q(groups__permissions=perm) | Q(user_permissions=perm)).distinct()
