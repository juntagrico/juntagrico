from juntagrico.util.settings import tinymce_lang


# Rich text field defaults

RICHTEXTFIELD_DEFAULT_SETTINGS = {
    'menubar': False,
    'plugins': 'link  lists',
    'toolbar': 'undo redo | bold italic | alignleft aligncenter alignright alignjustify | outdent indent | bullist numlist | link',
}

RICHTEXTFIELD_DEFAULT_MAILER_PROFILE = {
    'height': 500,
    'relative_urls': False,
    'remove_script_host': False,
    'valid_styles': {
        '*': 'color,text-align,font-size,font-weight,font-style,text-decoration'
    },
    'menubar': 'edit insert format',
    'menu': {
        'edit': {'title': 'Edit', 'items': 'undo redo | cut copy paste | selectall'},
        'insert': {'title': 'Insert', 'items': 'link'},
        'format': {'title': 'Format',
                   'items': 'bold italic underline strikethrough superscript subscript | formats | removeformat'}
    },
}


def sanitize_html(value):
    import nh3
    return nh3.clean(
        value or "",
        tags={
            "p", "div", "br",
            "strong", "b", "em", "i",
            "ul", "ol", "li",
            "blockquote",
            "a",
        },
        attributes={
            "a": {"href", "title", "target"},
            "*": {"style"},
        },
        filter_style_properties={"text-align", "padding-left"},
        url_schemes={"http", "https", "mailto"},
    )


def richtextfield_config(language=None, use_in_admin=False, admin: dict = None, mailer: dict = None, **profiles):
    """
    :param language: The `LANGUAGE_CODE` specified in django settings
    :param use_in_admin: If True admin text fields use rich text fields
    :param admin: setting dicts to configure the rich text field in admin interface.
    :param mailer: setting dicts to configure the rich text field in mailer.
    :param profiles: other richtextfield profile configurations.
    :return: a config dict for DJRICHTEXTFIELD_CONFIG
    """
    conf = {
        'js': ['juntagrico/external/tinymce/tinymce.min.js'],
        'init_template': 'djrichtextfield/init/tinymce.js',
        'settings': RICHTEXTFIELD_DEFAULT_SETTINGS,
        'profiles': profiles,
    }
    if language:
        conf['settings']['language'] = tinymce_lang(language)
    # update default mailer profile
    conf['profiles']['juntagrico.mailer'] = RICHTEXTFIELD_DEFAULT_MAILER_PROFILE | (mailer or {})
    # use richtext in admin if enabled and specify profile
    if use_in_admin or admin is not None:
        conf['profiles']['juntagrico.admin'] = admin or {}
    conf['sanitizer_profiles'] = {'juntagrico.admin': sanitize_html}
    return conf


# depot list defaults

DEPOT_LISTS = {
    'depotlist': 'exports/depotlist.html',
    'depot_overview': 'exports/depot_overview.html',
    'amount_overview': 'exports/amount_overview.html',
}


# Impersonation helper

def allow_group(group_name):
    """
    Example usage in settings.py:
    ```
    from juntagrico import defaults

    allow_impersonate = defaults.allow_group('impersonators')

    IMPERSONATE = {
        'CUSTOM_ALLOW': 'myapp.settings.allow_impersonate'
    }
    ```
    """
    def check(request):
        return request.user.groups.filter(name=group_name).exists()
    return check


# CUSTOM_USER_QUERYSET presets
# Example usage in settings.py:
# ```
# IMPERSONATE = {
#     'CUSTOM_USER_QUERYSET': 'juntagrico.defaults.unprivileged_only'
# }
# ```
def user_queryset(unless_superuser=True, **filters):
    def check(request):
        from django.contrib.auth.models import User
        if unless_superuser and request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(**filters)
    return check


nonstaff_only = user_queryset(is_superuser=False, is_staff=False)

nonpermitted_only = user_queryset(
    is_superuser=False,
    is_staff=False,
    groups__isnull=True,
    user_permissions__isnull=True,
)

unprivileged_only = user_queryset(
    is_superuser=False,
    is_staff=False,
    groups__isnull=True,
    user_permissions__isnull=True,
    member__coordinated_areas__isnull=True,
    member__coordinated_depots__isnull=True,
)


# Password validation
# recommended default validators

password_validators = [
    {
        'NAME': 'juntagrico.password_validation.AccountAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# vocabulary helpers

def german(**keys):
    gender = {'m': 0, 'f': 1, 'n': 2, 's': 2}
    this = ['dieser ', 'diese ', 'dieses ']
    your = ['dein ', 'deine ', 'dein ']
    the_acc = ['den ', 'die ', 'das ']
    no = ['kein ', 'keine ', 'kein ']

    if 'account' in keys:
        account, accounts, g = keys['account']
        g = gender[g]
        keys.update(
            {
                'account': account,
                'account_pl': accounts,
                'this_account': this[g] + account,
            }
        )
    if 'assignment' in keys:
        assignment, assignments, g = keys['assignment']
        g = gender[g]
        keys.update(
            {
                'assignment': assignment,
                'assignment_pl': assignments,
                'the_assignment_acc': the_acc[g] + assignment,
            }
        )
    if 'member_type' in keys:
        member_type, member_types, g = keys['member_type']
        g = gender[g]
        keys.update(
            {
                'member_type': member_type,
                'member_type_pl': member_types,
                'not_a_member_type': no[g] + member_type,
            }
        )
    if 'membership' in keys:
        membership, memberships, g = keys['membership']
        g = gender[g]
        keys.update(
            {
                'membership': membership,
                'membership_pl': memberships,
                'your_membership_acc': your[g] + membership,
            }
        )
    if 'share' in keys:
        share, shares, g = keys['share']
        g = gender[g]
        keys.update(
            {
                'share': share,
                'share_pl': shares,
                'this_share': this[g] + share,
                'this_share_acc': ['diesen ', 'diese ', 'dieses '][g] + share,
                'no_share': no[g] + share,
            }
        )
    if 'depot' in keys:
        depot, depots, g = keys['depot']
        g = gender[g]
        keys.update(
            {
                'depot': depot,
                'depot_pl': depots,
                'the_depot_acc': the_acc[g] + depot,
                'the_depot_dat': ['dem ', 'der ', 'dem '][g] + depot,
                'to_the_depot': ['zum ', 'zur ', 'zum '][g] + depot,
                'your_depot': your[g] + depot,
            }
        )
    if 'subscription' in keys:
        subscription, subscriptions, g = keys['subscription']
        g = gender[g]
        keys.update(
            {
                'subscription': subscription,
                'subscription_pl': subscriptions,
                'the_subscription': ['der ', 'die ', 'das '][g] + subscription,
                'the_subscription_acc': the_acc[g] + subscription,
                'no_subscription_acc': no[g] + subscription,
                'this_subscription_acc': ['diesen ', 'diese ', 'dieses '][g] + subscription,
                'this_subscription_dat': ['diesem ', 'dieser ', 'diesem '][g] + subscription,
                'your_subscription': your[g] + subscription,
                'your_subscription_acc': ['deinen ', 'deine ', 'dein '][g] + subscription,
                'your_subscription_dat': ['deinem ', 'deiner ', 'deinem '][g] + subscription,
                'another_subscription_dat': ['einem anderen ', 'einer anderen ', 'einem anderen '][g] + subscription,
                'with_active_subscription': ['mit aktivem ', 'mit aktiver ', 'mit aktivem '][g] + subscription,
            }
        )
    if 'co_member' in keys:
        co_member, co_members, _ = keys['co_member']
        keys.update(
            {
                'co_member': co_member,
                'co_member_pl': co_members,
            }
        )
    return keys


def french(**keys):
    """
    if the word starts with an H it is assumed to be a silent H (h muet).
    For "h aspiré" use capital a letter for the gender i.e. 'M' or 'F'
    """
    vowel_sound = 'aeiouhàâäéèêëïîôöœù'
    no = {'m': 'aucun ', 'f': 'aucune '}

    def starts_with_vowel(word, g):
        return g.islower() and word[0].lower() in vowel_sound

    def get_demonstrative(word, g):
        """Returns 'ce', 'cet', or 'cette'"""
        if g.lower() == 'f':  # feminine
            return f'cette {word}'
        return f'cet {word}' if starts_with_vowel(word, g) else f'ce {word}'

    def get_definite_article(word, g):
        """Returns 'le', 'la', or 'l\''"""
        if starts_with_vowel(word, g):
            return f"l'{word}"
        return f'le {word}' if g.lower() == 'm' else f'la {word}'

    def get_dative(word, g):
        """Returns 'au', 'à la' or 'à l\''"""
        if starts_with_vowel(word, g):
            return f"à l'{word}"
        return f'au {word}' if g.lower() == 'm' else f'à la {word}'

    def get_possessive(word, g):
        """Returns 'ton' or 'ta'"""
        if starts_with_vowel(word, g):
            return f'ton {word}'
        return f'ton {word}' if g.lower() == 'm' else f'ta {word}'

    if 'account' in keys:
        account, accounts, g = keys['account']
        keys.update(
            {
                'account': account,
                'account_pl': accounts,
                'this_account': get_demonstrative(account, g),
            }
        )
    if 'assignment' in keys:
        assignment, assignments, g = keys['assignment']
        keys.update(
            {
                'assignment': assignment,
                'assignment_pl': assignments,
                'the_assignment_acc': get_definite_article(assignment, g),
            }
        )
    if 'member_type' in keys:
        member_type, member_types, g = keys['member_type']
        keys.update(
            {
                'member_type': member_type,
                'member_type_pl': member_types,
                # 'pas' or 'plus' must be written in the translation of the expression
                'not_a_member_type': ('un ' if g.lower() == 'm' else 'une ') + member_type,
            }
        )
    if 'membership' in keys:
        membership, memberships, g = keys['membership']
        keys.update(
            {
                'membership': membership,
                'membership_pl': memberships,
                'your_membership_acc': get_possessive(membership, g),
            }
        )
    if 'share' in keys:
        share, shares, g = keys['share']
        keys.update(
            {
                'share': share,
                'share_pl': shares,
                'this_share': get_demonstrative(share, g),
                'this_share_acc': get_demonstrative(share, g),
                'no_share': no[g.lower()] + share,
            }
        )
    if 'depot' in keys:
        depot, depots, g = keys['depot']
        keys.update(
            {
                'depot': depot,
                'depot_pl': depots,
                'the_depot_acc': get_definite_article(depot, g),
                'the_depot_dat': get_dative(depot, g),
                'to_the_depot': 'vers ' + get_definite_article(depot, g),
                'your_depot': get_possessive(depot, g),
            }
        )
    if 'subscription' in keys:
        subscription, subscriptions, g = keys['subscription']
        keys.update(
            {
                'subscription': subscription,
                'subscription_pl': subscriptions,
                'the_subscription': get_definite_article(subscription, g),
                'the_subscription_acc': get_definite_article(subscription, g),
                'no_subscription_acc': no[g.lower()] + subscription,
                'this_subscription_acc': get_demonstrative(subscription, g),
                'this_subscription_dat': get_demonstrative(subscription, g),
                'your_subscription': get_possessive(subscription, g),
                'your_subscription_acc': get_possessive(subscription, g),
                'your_subscription_dat': get_possessive(subscription, g),
                'another_subscription_dat': (
                    f'à un autre {subscription}' if g.lower() == 'm' else f'à une autre {subscription}'
                ),
                'with_active_subscription': f'un {subscription} actif' if g.lower() == 'm' else f'une {subscription} active',
            }
        )
    if 'co_member' in keys:
        co_member, co_members, _ = keys['co_member']
        keys.update(
            {
                'co_member': co_member,
                'co_member_pl': co_members,
            }
        )
    return keys
