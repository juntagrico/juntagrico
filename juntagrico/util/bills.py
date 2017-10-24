from juntagrico.dao.extrasubbillingperioddao import ExtraSubBillingPeriodDao
from juntagrico.entity.billing import *
from juntagrico.entity.subs import *
from juntagrico.util.temporal import *
from juntagrico.config import Config
from juntagrico.mailer import *

def calculate_check_number(ref_number):
    numbers=[0, 9, 4, 6, 8, 2, 7, 1, 3, 5]
    overfloat = 0
    for n in ref_number:
        overfloat = numbers[(overfloat+int(n))%10]
    return str((10-overfloat)%10)

def generate_ref_number(type,billable_id,recipient_id,start=None):
    type_code = {'subscription':'01','share':'02','extra':'03'}.get(type,'00')
    start_code = '000000'
    if start is not None:
        start_code = start.strftime('%y%m%d')
    billable_code = str(billable_id).rjust(9,'0')
    recipient_code = str(recipient_id).rjust(9,'0')
    without_cs = type_code+billable_code+recipient_code+start_code
    cs = calculate_check_number(without_cs)
    return without_cs+cs


def bill_subscription(subscrtption):
    now = timezone.now()
    start = start_of_business_year()
    end = start_of_next_business_year()    
    ref_date = max(subscription.activation_date, start)
    total_days=(start-end).days-1
    remaining_days=(ref_date-end).days-1
    price = subscription.price*(remaining_days/total_days)
    refnumber = generate_ref_number('subscription',subscription.id,subscription.primary_member.id,start)
    bill = Bill.objects.create(billable=subscription,ammount=price,ref_number=refnumber,bill_date=now)
    send_bill_sub(bill, subscription, start, end, subscription.primary_member)


def bill_share(share):
    now = timezone.now()
    price = float(Config.share_price())
    refnumber = generate_ref_number('share',share.id,share.member.id)
    bill = Bill.objects.create(billable=share,ammount=price,ref_number=refnumber,bill_date=now)
    send_bill_share(bill, share, share.member)   


def bill_extra_subscription(extra):
    period = ExtraSubBillingPeriodDao.get_current_period_per_type(extra.type)
    bill_extra_subscription(extra, period)
    
    
def bill_extra_subscription(extra, period):
    price = period.calculated_price(extra.activation_date)
    start = period.get_actual_start(extra.activation_date)
    end = period.get_actual_end()
    refnumber = generate_ref_number('extra',extra.id,extra.main_subscription.primary_member.id,start)
    bill = Bill.objects.create(billable=extra,ammount=price,ref_number=refnumber,bill_date=now)
    send_bill_extrasub(bill, extra, start, end, extra.main_subscription.primary_member)
    