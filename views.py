import datetime

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
