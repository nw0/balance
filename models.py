from django.contrib.auth.models import User
from django.db import models
from djmoney.models.fields import MoneyField


class Account(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=30)
    owned = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AccountBalance(models.Model):
    owner = models.ForeignKey(User)
    account = models.ForeignKey(Account)
    balance = MoneyField(max_digits=16, decimal_places=2, default_currency="GBP")
    date = models.DateField()

    def __str__(self):
        return self.balance

    class Meta:
        verbose_name = "balance record"
