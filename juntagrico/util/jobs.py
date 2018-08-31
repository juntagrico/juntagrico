import math


def get_status_image(percent=0):
    status_number = min(100, int(25 * math.floor(float(percent)/25)))
    result = 'status_' + str(status_number)
    return result


def get_status_image_text(percent=0):
    texts = {
        100: 'Fertig',
        75: 'Dreivierte',
        50: 'Halb',
        25: 'Angefangen',
        0: 'Nix'
    }
    status_number = min(100, int(25 * math.floor(float(percent)/25)))
    return texts[status_number]
