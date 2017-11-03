def get_status_image(percent=0):
    if percent >= 100:
        return 'status_100'
    elif percent >= 75:
        return 'status_75'
    elif percent >= 50:
        return 'status_50'
    elif percent > 0:
        return 'status_25'
    else:
        return 'status_0'


def get_status_image_text(percent=0):
    if percent >= 100:
        return 'Fertig'
    elif percent >= 75:
        return 'Dreiviertel'
    elif percent >= 50:
        return 'Halb'
    elif percent > 0:
        return 'Angefangen'
    else:
        return 'Nix'
