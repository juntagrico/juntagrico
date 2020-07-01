from django.contrib.auth.decorators import user_passes_test


def chainable(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        return args[0]
    return wrapper


def any_permission_required(*perms):
    """
    Decorator for views that checks whether a user has any of the given permissions
    """
    def check_perms(user):
        # check if the user has any of the permission
        if set(user.get_all_permissions()) & set(perms):
            return True
        return False
    return user_passes_test(check_perms)
