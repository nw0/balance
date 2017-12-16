from django.contrib import admin

from .models import Account, AccountBalance, TransactionCategory, Transaction

admin.site.register(Account)
admin.site.register(AccountBalance)
admin.site.register(TransactionCategory)
admin.site.register(Transaction)
