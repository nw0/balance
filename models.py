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


class TransactionCategory(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"


class Transaction(models.Model):
    owner = models.ForeignKey(User)
    payee = models.ForeignKey(Account, blank=True)
    payer = models.ForeignKey(Account, blank=True)
    date = models.DateField()
    category = models.ForeignKey(TransactionCategory)
    remark = models.CharField(max_length=50)
    amount = MoneyField(max_digits=16, decimal_places=2, default_currency="GBP")

    def __str__(self):
        return "%s (%s: %s)" % (self.amount, self.category, self.remark)
