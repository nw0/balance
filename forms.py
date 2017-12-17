from django import forms

from .models import Account, Transaction, TransactionCategory, AccountBalance


class BalanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(BalanceForm, self).__init__(*args, **kwargs)

        self.fields['account'].queryset = Account.objects.filter(owner=user)

    class Meta:
        model = AccountBalance
        exclude = []


class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)

        self.fields['payee'].queryset = Account.objects.filter(owner=user)
        self.fields['payer'].queryset = Account.objects.filter(owner=user)
        self.fields['category'].queryset = TransactionCategory.objects.filter(owner=user)

    class Meta:
        model = Transaction
        exclude = ['owner']