import datetime

from django.contrib import messages
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import generic

from balance.models import Category


def months(start, times):
    # returns months backwards
    date, it = start, times
    while it > 0:
        date = datetime.date(date.year, date.month, 1)
        yield date
        it -= 1
        date -= datetime.timedelta(days=1)


class CategoryList(generic.ListView):
    model = Category

    def get_context_data(self, **kwargs):
        context = super(CategoryList, self).get_context_data(**kwargs)
        context['dates'] = [m for m in months(datetime.date.today(), 4)]
        return context


class CategoryCreate(generic.edit.CreateView):
    model = Category
    fields = ['name']
    success_url = reverse_lazy('balance:category_list')

    def form_valid(self, form):
        if "_add_another" in self.request.POST:
            self.success_url = reverse('balance:category_create')
        messages.success(self.request, "Created %s" %
            (form.instance,))
        form.instance.owner = self.request.user
        return super(CategoryCreate, self).form_valid(form)
