from django import template

register = template.Library()


@register.filter
def overview(part_overview):
    def loop(result_list, key, value, more_than_one=False):
        if more_than_one:
            result_list.append('<li>{}</li>'.format(key))
            result_list.append('<ul>')
        for new_key, new_value in value.items():
            if isinstance(new_value, int):
                display_name = new_key[1] if new_key[1] != '' else key
                result_list.append('<li> {}× {} </li>'.format(new_value, display_name))
            else:
                loop(result_list, new_key, new_value, len(value.items()) > 1)
        if more_than_one:
            result_list.append('</ul>')

    result = ['<ul>']
    loop(result, '', part_overview)
    result.append('</ul>')
    return '\n'.join(result)


@register.simple_tag
def price_summary(subscription, parts, surcharges):
    part_summary = {part: part.price for part in parts}
    surcharge_summary = {surcharge: surcharge.amount for surcharge in surcharges}
    depot_fees = {
        conditions.subscription_type_id: conditions.fee
        for conditions in subscription.depot.subscription_type_conditions.all() if conditions.fee != 0
    }
    depot_fee_summary = {
        part: depot_fees[part.type_id]
        for part in parts if part.type_id in depot_fees
    }
    summary = {
        'parts_total': sum(part_summary.values()),
        'depot_fee_total': sum(depot_fee_summary.values()) + subscription.depot.fee,
        'surcharges_total': sum(surcharge_summary.values()),
    }
    return {
        'parts': part_summary,
        'surcharges': surcharge_summary,
        'depot_fee_by_type': depot_fee_summary,
        'depot_fee_general': subscription.depot.fee,
        'total': sum(summary.values()),
        **summary,
    }
