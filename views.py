from datetime import date

from django.db.models import Sum, Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
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


def category_redirect(request, pk):
    return HttpResponseRedirect(reverse('balance:category_month', kwargs={'category_pk': pk,
                                                                          'year': date.today().strftime("%Y"),
                                                                          'month': date.today().strftime("%m")}))


class CategoryMonth(generic.dates.MonthArchiveView):
    allow_empty = True
    allow_future = True
    date_field = "date"

    def dispatch(self, request, *args, **kwargs):
        self.category = TransactionCategory.objects.get(pk=kwargs.get('category_pk', None))
        return super(CategoryMonth, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Transaction.objects.filter(category__owner=self.request.user, category=self.category)

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryMonth, self).get_context_data(*args, **kwargs)
        context['category'] = self.category
        context['total'] = 0
        for t in self.object_list:
            if not t.internal:
                context['total'] += t.internal_change
        return context


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
