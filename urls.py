from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.CategoryList.as_view(), name="index"),
    url(r'^$', views.CategoryList.as_view(), name="category_list"),
    url(r'^categories/new/$', views.CategoryCreate.as_view(), name="category_create"),
    url(r'^transactions/new/$', views.EntryCreate.as_view(), name="entry_create"),
    url(r'^transactions/$', views.entry_redirect, name="entry"),

    url(r'^transactions/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/$',
        views.EntryMonthArchive.as_view(month_format="%m"),
        name="entry_month"),
]
