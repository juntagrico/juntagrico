from datetime import date, timedelta
from django.utils import timezone

from juntagrico.dao.extrasubbillingperioddao import ExtraSubBillingPeriodDao
from juntagrico.entity.billing import Bill
from juntagrico.util.temporal import start_of_next_business_year
from juntagrico.util.temporal import start_of_specific_business_year
from juntagrico.util.temporal import end_of_specific_business_year
from juntagrico.util.temporal import start_of_business_year
from juntagrico.config import Config
from juntagrico.mailer import send_bill_extrasub
from juntagrico.mailer import send_bill_sub
from juntagrico.mailer import send_bill_share


type_codes = {'subscription': '01', 'share': '02', 'extra': '03'}


def calculate_check_number(ref_number):
    numbers = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5]
    overfloat = 0
    for n in ref_number:
        overfloat = numbers[(overfloat+int(n)) % 10]
    return str((10-overfloat) % 10)


def generate_ref_number(type, billable_id, recipient_id, start=None):
    type_code = type_codes.get(type, '00')
    start_code = '000000'
    if start is not None:
        start_code = start.strftime('%y%m%d')
    billable_code = str(billable_id).rjust(9, '0')
    recipient_code = str(recipient_id).rjust(9, '0')
    without_cs = type_code+billable_code+recipient_code+start_code
    cs = calculate_check_number(without_cs)
    return without_cs+cs


def scale_subscription_price(subscription, fromdate, tilldate):
    """
    scale subscription price for a certain date interval.
    """
    year_price = subscription.price

    start_of_year = start_of_specific_business_year(fromdate)
    end_of_year = end_of_specific_business_year(fromdate)

    if tilldate > end_of_year:
        raise Exception("till-date is not in same business year as from-date")

    days_year = (end_of_year - start_of_year).days + 1
    subs_start = max(subscription.activation_date or date.min, fromdate)
    subs_end = min(subscription.deactivation_date or date.max, tilldate)
    days_subs = (subs_end - subs_start).days + 1

    return year_price * days_subs / days_year


def bill_subscription(subscription):
    now = timezone.now()
    start = start_of_business_year()
    end = start_of_next_business_year()
    price = scale_subscription_price(subscription,
                                     start_of_business_year(), end_of_business_year() - timedelta(1))

    refnumber = generate_ref_number('subscription',
                                    subscription.id,
                                    subscription.primary_member.id,
                                    start)

    bill = Bill.objects.create(billable=subscription,
                               amount=price,
                               ref_number=refnumber,
                               bill_date=now)
    send_bill_sub(bill, subscription, start, end, subscription.primary_member)


def bill_share(share):
    now = timezone.now()
    price = float(Config.share_price())
    refnumber = generate_ref_number('share', share.id, share.member.id)
    bill = Bill.objects.create(billable=share,
                               amount=price,
                               ref_number=refnumber,
                               bill_date=now)
    send_bill_share(bill, share, share.member)


def bill_extra_subscription(extra):
    period = ExtraSubBillingPeriodDao.get_current_period_per_type(extra.type)
    bill_extra_subscription(extra, period)


def bill_extra_subscription(extra, period):
    now = timezone.now
    price = period.calculated_price(extra.activation_date)
    start = period.get_actual_start(extra.activation_date)
    end = period.get_actual_end()
    refnumber = generate_ref_number('extra',
                                    extra.id,
                                    extra.main_subscription.primary_member.id,
                                    start)
    bill = Bill.objects.create(billable=extra,
                               amount=price,
                               ref_number=refnumber,
                               bill_date=now)
    member = extra.main_subscription.primary_member
    send_bill_extrasub(bill, extra, start, end, member)
