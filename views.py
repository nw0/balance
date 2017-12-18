from django.urls import reverse_lazy
from django.views import generic

from .forms import TransactionForm, BalanceForm
from .models import Account, TransactionCategory, Transaction, AccountBalance


class AccountList(generic.ListView):
    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(AccountList, self).get_context_data(**kwargs)

        context['owned_accounts'] = context['object_list'].filter(owned=True)
        context['other_accounts'] = context['object_list'].filter(owned=False)
        return context


class AccountDetail(generic.DetailView):
    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(AccountDetail, self).get_context_data(**kwargs)

        context['balance_form'] = BalanceForm(user=self.request.user, hide_account=True, initial={'account': self.object})
        return context


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

    def get_success_url(self):
        return reverse_lazy('balance:account_detail', args=[self.object.account.pk])


class CategoryList(generic.ListView):
    def get_queryset(self):
        return TransactionCategory.objects.filter(owner=self.request.user)


class CategoryDetail(generic.DetailView):
    def get_queryset(self):
        return TransactionCategory.objects.filter(owner=self.request.user)


class CategoryCreate(generic.edit.CreateView):
    model = TransactionCategory
    fields = ['name']
    success_url = reverse_lazy('balance:category_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(CategoryCreate, self).form_valid(form)


class TransactionCreate(generic.edit.CreateView):
    model = Transaction
    form_class = TransactionForm
    success_url = reverse_lazy('balance:transaction_create')

    def get_form_kwargs(self):
        kwargs = super(TransactionCreate, self).get_form_kwargs()

        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(TransactionCreate, self).form_valid(form)
