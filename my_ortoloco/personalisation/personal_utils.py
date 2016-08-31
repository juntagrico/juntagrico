def enrich_menu_dict(request, menu_dict):
    menu_dict.update({    
        'politoloco': request.user.has_perm('static_ortoloco.can_send_newsletter')
    })