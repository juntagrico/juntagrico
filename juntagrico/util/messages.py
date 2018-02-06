# -*- coding: utf-8 -*-

from django.template.loader import get_template

from juntagrico.dao.sharedao import ShareDao

def messages(request):
    result = []
    member = request.user.member
    if member.confirmed is False:
        result.append(get_template('messages/not_confirmed.html').render())
        
    if member.subscription is None and member.future_subscription is None:
        result.append(get_template('messages/no_subscription.html').render())
        
    if len(ShareDao.unpaid_shares(member))>0:
        render_dict ={
            'amount': len(ShareDao.unpaid_shares(member)),
        }
        result.append(get_template('messages/unpaid_shares.html').render(render_dict))
    
    return result