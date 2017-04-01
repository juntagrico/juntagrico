def get_status_image(percent=0):
    if percent >= 100:
        return "circle_full"
    elif percent >= 75:
        return "circle_alomst_full"
    elif percent >= 50:
        return "circle_half"
    elif percent > 0:
        return "circle_almost_empty"
    else:
        return "circle_empty"


def get_status_image_text(percent=0):
    if percent >= 100:
        return "Fertig"
    elif percent >= 75:
        return "Dreiviertel"
    elif percent >= 50:
        return "Halb"
    elif percent > 0:
        return "Angefangen"
    else:
        return "Nix"
