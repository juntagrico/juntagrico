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
    part_summary = {part: part.type.price for part in parts}
    surcharge_summary = {surcharge: surcharge.amount for surcharge in surcharges}
    summary = {
        'parts_total': sum(part_summary.values()),
        'depot_fee': subscription.depot.fee,
        'surcharges_total': sum(surcharge_summary.values()),
    }
    return {
        'parts': part_summary,
        'surcharges': surcharge_summary,
        'total': sum(summary.values()),
        **summary,
    }
