from django.views import generic

from .models import Account


class AccountList(generic.ListView):
    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user)
