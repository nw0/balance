from django import template
from django.urls import reverse

register = template.Library()


@register.filter()
def other_account(transaction, account):
    return transaction.payee if account == transaction.payer else transaction.payer


@register.filter()
def net_amount(transaction, account):
    return transaction.net_amount(account)


@register.simple_tag
def nav_active(request, url, *args):
    if reverse(url, args=args) in request.path:
        return "active"
    return ""
