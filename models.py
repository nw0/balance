from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from djmoney.models.fields import MoneyField


@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(User)

    def monthly(self, date):
        sum = Entry.objects.filter(category=self, date__year=date.year, date__month=date.month).aggregate(models.Sum('amount'))['amount__sum']
        return sum or 0

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Entry(models.Model):
    INCOME, EXPENSE = 0, 1
    TRANSACTION_TYPES = (
        (INCOME, "Income"),
        (EXPENSE, "Expenditure"),
    )
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPES)
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency="GBP")
    date = models.DateField()
    note = models.CharField(max_length=50)
    category = models.ForeignKey(Category)

    class Meta:
        verbose_name_plural = "entries"

    def __str__(self):
        return "%s %s: [%s] %s %s" % (
            self.date, self.get_transaction_type_display(), self.category, self.note, self.amount)
