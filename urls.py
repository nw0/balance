from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.CategoryList.as_view(), name="index"),
    url(r'^$', views.CategoryList.as_view(), name="category_list"),
]
