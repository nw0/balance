from datetime import date
from django import forms

from .models import (Account, Transaction, TransactionCategory, AccountBalance,
                     Budget, BudgetAllocation)


class BalanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        hide_account = kwargs.pop('hide_account', False)
        super(BalanceForm, self).__init__(*args, **kwargs)

        self.fields['account'].queryset = Account.objects.filter(owner=user)
        if hide_account:
            self.fields['account'].widget = forms.HiddenInput()

    class Meta:
        model = AccountBalance
        exclude = []


class TransactionForm(forms.ModelForm):
    # TODO: only allow account currencies

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)

        self.fields['payee'].queryset = Account.objects.filter(owner=user)
        self.fields['payer'].queryset = Account.objects.filter(owner=user)
        self.fields['category'].queryset = TransactionCategory.objects.filter(owner=user)
        self.fields['date'].initial = date.today()

    class Meta:
        model = Transaction
        exclude = ['owner']


class BudgetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(BudgetForm, self).__init__(*args, **kwargs)

        self.fields['accounts'].queryset = Account.objects.filter(owner=user,owned=True)

    class Meta:
        model = Budget
        exclude = ['owner', 'categories']


class AllocationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        budget_pk = kwargs.pop('budget_pk', None)
        budget = Budget.objects.get(pk=budget_pk)
        user = kwargs.pop('user', None)
        if user != budget.owner:
            raise ValueError("Invalid budget")
        super(AllocationForm, self).__init__(*args, **kwargs)

        self.fields['category'].queryset = TransactionCategory.objects.filter(owner=user)
        self.fields['budget'].queryset = Budget.objects.filter(owner=user)
        self.fields['budget'].initial = budget

    class Meta:
        model = BudgetAllocation
        exclude = []
