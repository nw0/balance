from datetime import date
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, Sum
from djmoney.models.fields import MoneyField


class Account(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    owned = models.BooleanField(default=True)

    @property
    def related_balances(self):
        return AccountBalance.objects.filter(account=self)

    @property
    def last_balance(self):
        return self.related_balances.latest()

    @property
    def balance_estimate(self):
        last = self.last_balance
        balance = last.balance

        for transaction in self.related_transactions.filter(date__gt=last.date):
            balance += transaction.net_amount(self)
        return balance

    @property
    def recent_transactions(self):
        return self.related_transactions.order_by("-date", "-pk")

    @property
    def related_transactions(self):
        return Transaction.objects.filter(Q(payee=self) | Q(payer=self))

    def transactions_between(self, date_start, date_end):
        """Transactions t: `date_bef` <= t.date < `date_end`"""
        return self.related_transactions.filter(date__range=(date_start, date_end))

    def categorise(self, date_start, date_end):
        categories = {}
        for t in self.transactions_between(date_start, date_end):
            categories.setdefault(t.category, 0)
            categories[t.category] += t.net_amount(self)
        return categories

    def balance_after(self, transaction):
        balance = AccountBalance.objects.filter(account=self, date__lt=transaction.date).order_by('-date').first()
        if not balance:
            return None

        value = balance.balance
        for t in self.related_transactions.filter(date__gt=balance.date, date__lte=transaction.date):
            if t.date < transaction.date or t.pk <= transaction.pk:
                value += t.net_amount(self)
        return value

    def find_discrepancies(self, date_start, date_end):
        balances = self.related_balances.filter(date__range=(date_start, date_end))
        return [(b,d) for (b, d) in ((b, b.difference) for b in balances) if d]

    def __str__(self):
        return self.name


class AccountBalance(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance = MoneyField(max_digits=16, decimal_places=2, default_currency="GBP")
    date = models.DateField()

    @property
    def last_transaction(self):
        return self.account.related_transactions.filter(date__lte=self.date).order_by('-date', '-pk').first()

    @property
    def previous_record(self):
        return AccountBalance.objects.filter(account=self.account, date__lt=self.date).order_by('-date').first()

    @property
    def difference(self):
        expected = None
        if self.last_transaction is not None:
            expected = self.account.balance_after(self.last_transaction)
        elif self.previous_record is not None:
            expected = self.previous_record.balance
        if expected is not None:
            return self.balance - expected
        return None

    def __str__(self):
        return str(self.balance)

    class Meta:
        get_latest_by = "date"
        verbose_name = "balance record"


class TransactionCategory(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    def month_change(self):
        changes = {}
        for transaction in Transaction.objects.filter(category=self, date__gte=date.today().replace(day=1)):
            currency = transaction.amount.currency
            if currency not in changes:
                changes[currency] = 0
            changes[currency] += transaction.net_change
        return changes

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

    @property
    def internal(self):
        return self.payee.owned and self.payer.owned

    @property
    def internal_change(self):
        # neg if paid someone else, pos oth: see category Internal
        return self.amount * (-1 if self.payer.owned and not self.payee.owned else 1)

    @property
    def net_change(self):
        # Paid someone else or vice-versa
        if self.payer.owned and not self.payee.owned:
            return -1 * self.amount
        elif not self.payer.owned and self.payee.owned:
            return self.amount
        else:
            return 0

    def net_amount(self, account):
        # Flows from an account
        return self.amount * (-1 if account == self.payer else 1)

    def __str__(self):
        return "%s (%s: %s)" % (self.amount, self.category, self.remark)

    class Meta:
        get_latest_by = ["date", "pk"]


class Budget(models.Model):
    EXPENDITURE = 0
    ALLOCATION = 1

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    accounts = models.ManyToManyField(Account)
    remark = models.TextField()
    date_start = models.DateField()
    date_end = models.DateField()
    categories = models.ManyToManyField(TransactionCategory, through="BudgetAllocation")

    def categorise(self):
        categories, totals = {}, {}
        # {Category: {Currency: {EXP: 3, ALLOC: 5}}

        for account in self.accounts.all():
            for c, s in account.categorise(self.date_start, self.date_end).items():
                currency = categories.setdefault(c, {}).setdefault(s.currency, {})
                currency.setdefault(Budget.EXPENDITURE, 0)
                currency[Budget.EXPENDITURE] += s
                currency = totals.setdefault(s.currency, {})
                currency.setdefault(Budget.EXPENDITURE, 0)
                currency[Budget.EXPENDITURE] += s

        for alloc in self.budgetallocation_set.all():
            currency = categories.setdefault(alloc.category, {}).setdefault(alloc.amount.currency, {})
            currency.setdefault(Budget.ALLOCATION, 0)
            currency[Budget.ALLOCATION] += alloc.amount
            currency = totals.setdefault(alloc.amount.currency, {})
            currency.setdefault(Budget.ALLOCATION, 0)
            currency[Budget.ALLOCATION] += alloc.amount
        return categories, totals

    def __str__(self):
        return self.name


class BudgetAllocation(models.Model):
    budget = models.ForeignKey(Budget,on_delete=models.CASCADE)
    category = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE)
    amount = MoneyField(max_digits=16, decimal_places=2, default_currency="GBP")

    @property
    def owner(self):
        return self.budget.owner

    def __str__(self):
        return "%s (%s)" % (self.category, self.amount)
