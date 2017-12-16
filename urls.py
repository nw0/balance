from django.urls import path

from . import views

app_name = 'balance'
urlpatterns = [
    path('', views.AccountList.as_view(), name='account_list'),
    path('account/create/', views.AccountCreate.as_view(), name='account_create'),
    path('category/create/', views.CategoryCreate.as_view(), name='category_create'),
]
