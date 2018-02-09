from django.contrib import admin

from .models import (Account, AccountBalance, TransactionCategory, Transaction,
                     Budget, BudgetAllocation)

admin.site.register(Account)
admin.site.register(AccountBalance)
admin.site.register(TransactionCategory)
admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(BudgetAllocation)
