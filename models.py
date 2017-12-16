from django.contrib.auth.models import User
from django.db import models
from djmoney.models.fields import MoneyField


class Account(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    owned = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AccountBalance(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance = MoneyField(max_digits=16, decimal_places=2, default_currency="GBP")
    date = models.DateField()

    def __str__(self):
        return self.balance

    class Meta:
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
    remark = models.CharField(max_length=50)
    amount = MoneyField(max_digits=16, decimal_places=2, default_currency="GBP")

    def __str__(self):
        return "%s (%s: %s)" % (self.amount, self.category, self.remark)
