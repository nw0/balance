from django.urls import reverse_lazy
from django.views import generic

from .forms import TransactionForm, BalanceForm
from .models import Account, TransactionCategory, Transaction, AccountBalance


class AccountList(generic.ListView):
    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user)


class AccountDetail(generic.DetailView):
    model = Account

    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user)


class AccountCreate(generic.edit.CreateView):
    model = Account
    fields = ['name', 'owned']
    success_url = reverse_lazy('balance:account_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(AccountCreate, self).form_valid(form)


class BalanceUpdate(generic.edit.CreateView):
    model = AccountBalance
    form_class = BalanceForm

    # FIXME: redirect to appropriate account detail page
    success_url = reverse_lazy('balance:account_list')

    def get_form_kwargs(self):
        kwargs = super(BalanceUpdate, self).get_form_kwargs()

        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        record = AccountBalance.objects.filter(account=form.instance.account, date=form.instance.date).first()
        if record is not None:
            record.balance = form.instance.balance
            form.instance = record
        return super(BalanceUpdate, self).form_valid(form)


class CategoryCreate(generic.edit.CreateView):
    model = TransactionCategory
    fields = ['name']
    success_url = reverse_lazy('balance:account_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(CategoryCreate, self).form_valid(form)


class TransactionCreate(generic.edit.CreateView):
    model = Transaction
    form_class = TransactionForm
    success_url = reverse_lazy('balance:account_list')

    def get_form_kwargs(self):
        kwargs = super(TransactionCreate, self).get_form_kwargs()

        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(TransactionCreate, self).form_valid(form)
