from django import template

register = template.Library()


@register.filter()
def other_account(transaction, account):
    return transaction.payee if account == transaction.payer else transaction.payer


@register.filter()
def net_amount(transaction, account):
    return transaction.net_amount(account)
