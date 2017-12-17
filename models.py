from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from djmoney.models.fields import MoneyField


class Account(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    owned = models.BooleanField(default=True)

    @property
    def last_balance(self):
        return AccountBalance.objects.filter(account=self).latest()

    @property
    def balance_estimate(self):
        last = self.last_balance
        balance = last.balance

        for transaction in self.related_transactions.filter(date__gt=last.date):
            balance += transaction.net_amount(self)
        return balance

    @property
    def recent_transactions(self):
        return self.related_transactions.order_by("-date")

    @property
    def related_transactions(self):
        return Transaction.objects.filter(Q(payee=self) | Q(payer=self))

    def __str__(self):
        return self.name


class AccountBalance(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance = MoneyField(max_digits=16, decimal_places=2, default_currency="GBP")
    date = models.DateField()

    def __str__(self):
        return str(self.balance)

    class Meta:
        get_latest_by = "date"
        verbose_name = "balance record"


class TransactionCategory(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"


class Transaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    payee = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="payee", blank=True)
    payer = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="payer",  blank=True)
    date = models.DateField()
    category = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE)
    remark = models.CharField(max_length=50, blank=True)
    amount = MoneyField(max_digits=16, decimal_places=2, default_currency="GBP")

    def net_amount(self, account):
        return self.amount * (-1 if account == self.payer else 1)

    def __str__(self):
        return "%s (%s: %s)" % (self.amount, self.category, self.remark)

    class Meta:
        get_latest_by = "date"
