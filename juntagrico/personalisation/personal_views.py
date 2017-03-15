from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from juntagrico.views import get_menu_dict
from juntagrico.models import *

from .personal_mailer import *

#from static_ortoloco.models import Politoloco

@permission_required('static_ortoloco.can_send_newsletter')
def send_politoloco(request):
    """
    Send politoloco newsletter
    """
    sent = 0
    if request.method == 'POST':
        emails = set()
        if request.POST.get("allpolitoloco"):
            print "geilescheiss 1"
            for loco in Politoloco.objects.all():
                emails.add(loco.email)

        if request.POST.get("allmembers"):
            for loco in Member.objects.all():
                emails.add(loco.email)

        if request.POST.get("allsingleemail"):
            emails.add(request.POST.get("singleemail"))

        index = 1
        attachements = []
        while request.FILES.get("image-" + str(index)) is not None:
            attachements.append(request.FILES.get("image-" + str(index)))
            index += 1

        send_politoloco_mail(request.POST.get("subject"), request.POST.get("message"), request.POST.get("textMessage"), emails, request.META["HTTP_HOST"], attachements)
        sent = len(emails)
    renderdict = get_menu_dict(request)
    renderdict.update({
        'politolocos': Politoloco.objects.count(),
        'members': Member.objects.count(),
        'sent': sent
    })
    return render(request, 'mail_sender_politoloco.html', renderdict)
