from django import template
from django.urls import reverse

from ..models import Account, Budget

register = template.Library()


@register.filter()
def other_account(transaction, account):
    return transaction.payee if account == transaction.payer else transaction.payer


@register.filter()
def net_amount(transaction, account):
    return transaction.net_amount(account)


@register.filter()
def discrepancies(account: Account, budget: Budget):
    return sum ((s for b, s in account.find_discrepancies(budget.date_start, budget.date_end)))


@register.simple_tag
def nav_active(request, url, *args):
    if reverse(url, args=args) in request.path:
        return "active"
    return ""
