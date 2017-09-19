# -*- coding: utf-8 -*-

from django.template.loader import get_template

from juntagrico.dao.sharedao import ShareDao

def messages(request):
    result = []
    if request.user.member.confirmed is False:
        result.append(get_template('messages/not_confirmed.html').render())
        
    if request.user.member.subscription is None:
        result.append(get_template('messages/no_subscription.html').render())
        
    if len(ShareDao.unpaid_shares(request.user.member))>0:
        render_dict ={
            'amount': len(ShareDao.unpaid_shares(request.user.member)),
        }
        result.append(get_template('messages/unpaid_shares.html').render(render_dict))
    
    return result