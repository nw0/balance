from datetime import date

from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views import generic

from .forms import TransactionForm, BalanceForm, BudgetForm, AllocationForm
from .models import (Account, TransactionCategory, Transaction, AccountBalance,
                     Budget, BudgetAllocation)


class AccountList(generic.ListView):
    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(AccountList, self).get_context_data(**kwargs)

        context['owned_accounts'] = context['object_list'].filter(owned=True)
        context['other_accounts'] = context['object_list'].filter(owned=False)
        return context


def account_redirect(request, pk):
    return HttpResponseRedirect(reverse('balance:account_month', kwargs={'account_pk': pk,
                                                                         'year': date.today().strftime("%Y"),
                                                                         'month': date.today().strftime("%m")}))


class AccountMonth(generic.dates.MonthArchiveView):
    allow_empty = True
    allow_future = True
    date_field = "date"
    template_name = 'balance/account_archive_month.html'

    def dispatch(self, request, *args, **kwargs):
        self.account = Account.objects.get(pk=kwargs.get('account_pk', None), owner=request.user)
        return super(AccountMonth, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Transaction.objects.filter(category__owner=self.request.user).filter(Q(payee=self.account) | Q(payer=self.account)).order_by('-date', '-pk')

    def get_context_data(self, *args, **kwargs):
        context = super(AccountMonth, self).get_context_data(*args, **kwargs)
        context['balance_form'] = BalanceForm(user=self.request.user, hide_account=True, initial={'account': self.account})
        context['account'] = self.account
        context['total'] = {}
        balance = None
        for t in reversed(self.object_list):
            change = t.net_amount(self.account)
            if change:
                if change.currency not in context['total']:
                    context['total'][change.currency] = 0
                context['total'][change.currency] += change

            if balance is None:
                balance = self.account.balance_after(t)
            elif change:
                balance += change
            t.balance_after = balance
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
    template_name = 'balance/category_archive_month.html'

    def dispatch(self, request, *args, **kwargs):
        self.category = TransactionCategory.objects.get(pk=kwargs.get('category_pk', None), owner=request.user)
        return super(CategoryMonth, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Transaction.objects.filter(category__owner=self.request.user, category=self.category).order_by('-date', '-pk')

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryMonth, self).get_context_data(*args, **kwargs)
        context['category'] = self.category
        context['total'] = {}
        for t in self.object_list:
            change = t.net_change
            if change:
                if change.currency not in context['total']:
                    context['total'][change.currency] = 0
                context['total'][change.currency] += change
        return context


class CategoryCreate(generic.edit.CreateView):
    model = TransactionCategory
    fields = ['name']
    success_url = reverse_lazy('balance:category_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(CategoryCreate, self).form_valid(form)


class TransactionDetail(generic.DetailView):
    model = Transaction

    def get_queryset(self):
        return Transaction.objects.filter(category__owner=self.request.user)


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


class TransactionUpdate(generic.edit.UpdateView):
    model = Transaction
    form_class = TransactionForm

    def get_form_kwargs(self):
        kwargs = super(TransactionUpdate, self).get_form_kwargs()

        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(TransactionUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('balance:transaction_detail', args=[self.object.pk])


class TransactionDelete(generic.edit.DeleteView):
    model = Transaction

    def get_success_url(self):
        return reverse_lazy('balance:category_month', args=[self.object.category.pk, self.object.date.year, self.object.date.month])


class BudgetList(generic.ListView):
    def get_queryset(self):
        return Budget.objects.filter(owner=self.request.user)


class BudgetDetail(generic.DetailView):
    def get_queryset(self):
        return Budget.objects.filter(owner=self.request.user)


class BudgetCreate(generic.edit.CreateView):
    model = Budget
    form_class = BudgetForm
    success_url = reverse_lazy('balance:budget_list')

    def get_form_kwargs(self):
        kwargs = super(BudgetCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(BudgetCreate, self).form_valid(form)


class AllocationCreate(generic.edit.CreateView):
    model = BudgetAllocation
    form_class = AllocationForm

    def get_form_kwargs(self):
        kwargs = super(AllocationCreate, self).get_form_kwargs()
        kwargs['budget_pk'] = self.kwargs['budget_pk']
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('balance:budget_detail', args=[self.object.budget.pk])
