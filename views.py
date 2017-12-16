from django.urls import reverse_lazy
from django.views import generic

from .models import Account, TransactionCategory


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


class CategoryCreate(generic.edit.CreateView):
    model = TransactionCategory
    fields = ['name']
    success_url = reverse_lazy('balance:account_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(CategoryCreate, self).form_valid(form)
