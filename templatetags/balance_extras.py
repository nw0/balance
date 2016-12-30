import datetime
import numbers

from django import template
from django.utils.safestring import mark_safe
from moneyed import Money

register = template.Library()


def months(start, times):
    # returns months backwards
    date, it = start, times
    while it > 0:
        date = datetime.date(date.year, date.month, 1)
        yield date
        it -= 1
        date -= datetime.timedelta(days=1)


@register.filter(is_safe=True)
def accountform(value):
    currency = ""
    if isinstance(value, Money):
        currency = " %s" % value.currency
        value = value.amount
    if not isinstance(value, (numbers.Number, Money)):
        return ""
    if value > 0:
        return mark_safe("%s%s" % (value, currency))
    return mark_safe('<span class="text-danger">(%s%s)</span>' % (-value, currency))


@register.inclusion_tag('balance/embeds/cat_tr.html')
def cat_tr(category):
    dates = list(months(datetime.datetime.today(), 4))
    ret = {'category': category,
           'current': category.monthly(dates[0]),
           'first': category.monthly(dates[1]),
           'second': category.monthly(dates[2]),
           'third': category.monthly(dates[3]), }
    print(ret)
    ret['mean'] = (ret['first'] + ret['second'] + ret['third']) / 3
    return ret
