def get_main_member(request):
    if request.user.is_authenticated:
        main_member = request.user.member
    else:
        main_member = request.session.get('main_member')
    return main_member
