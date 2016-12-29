from django.views import generic

from balance.models import Category, Entry


class CategoryList(generic.ListView):
    model = Category