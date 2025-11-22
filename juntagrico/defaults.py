from juntagrico.util.settings import tinymce_lang


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
    return conf
