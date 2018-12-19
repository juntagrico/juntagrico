from juntagrico.config import Config

"""
    c means case
"""


def enriched_organisation(c):
    g = Config.organisation_name_config()['gender']
    if (c == 'N' and g == 'M') or ((c == 'G' or c == 'D') and g == 'F'):
        article = 'der'
    elif c == 'G' and (g == 'M' or g == 'N'):
        article = 'des'
    elif c == 'D' and (g == 'M' or g == 'N'):
        article = 'dem'
    elif c == 'A' and g == 'M':
        article = 'den'
    elif (c == 'N' or c == 'A') and g == 'F':
        article = 'die'
    elif (c == 'N' or c == 'A') and g == 'N':
        article = 'des'
    else:
        article = ''

    name = article + ' ' + \
        Config.organisation_name_config(
        )['type'] + ' ' + Config.organisation_name()

    return name.strip()
