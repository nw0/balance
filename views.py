import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import generic

from balance.forms import EntryForm
from balance.models import Category, Entry


def months(start, times):
    # returns months backwards
    date, it = start, times
    while it > 0:
        date = datetime.date(date.year, date.month, 1)
        yield date
        it -= 1
        date -= datetime.timedelta(days=1)


def entry_redirect(request):
    return HttpResponseRedirect(reverse('balance:entry_month', kwargs={'year': datetime.date.today().strftime("%Y"),
                                                                       'month': datetime.date.today().strftime("%m")}))


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


class EntryMonthArchive(generic.dates.MonthArchiveView):
    date_field = "date"
    allow_empty, allow_future = True, True

    def get_queryset(self):
        return Entry.objects.filter(category__owner=self.request.user).order_by('category')

    def get_context_data(self, **kwargs):
        context = super(EntryMonthArchive, self).get_context_data(**kwargs)
        context['entry_form'] = EntryForm
        return context


class EntryCreate(generic.edit.CreateView):
    model = Entry
    fields = ['amount', 'date', 'note', 'category']
    success_url = reverse_lazy('balance:entry')
