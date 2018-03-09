

def append_attachements(request, attachements):
    index = 1
    while request.FILES.get('image-' + str(index)) is not None:
        attachements.append(request.FILES.get('image-' + str(index)))
        index += 1
