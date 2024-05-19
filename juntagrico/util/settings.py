from pathlib import Path


def tinymce_lang(lang_code):
    """ Check if tinymce language matching passed language code is available
    :param lang_code: language_code from settings
    :return: matching name of language file for tinymce or None
    """
    lang_code = lang_code.lower().replace('-', '_')
    lang_path = Path(__file__).parent.parent / 'static/juntagrico/external/tinymce/langs'
    available_languages = [lang.stem for lang in lang_path.glob('*.js')]
    if lang_code in available_languages:
        return lang_code
    elif lang_code[:2] in available_languages:
        return lang_code[:2]
    return None
