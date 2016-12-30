import datetime

from django import template

register = template.Library()


@register.inclusion_tag('balance/embeds/cat_tr.html')
def cat_tr(category):
    today = datetime.datetime.today()
    return {'category': category,
            'current': today,
            'mean': '-',
            'third': '-',
            'second': '-',
            'first': '-'}
