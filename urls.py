from django.urls import path

from . import views

app_name = 'balance'
urlpatterns = [
    path('', views.AccountList.as_view(), name='account_list'),
    path('account/create/', views.AccountCreate.as_view(), name='account_create'),
    path('account/<int:pk>/', views.AccountDetail.as_view(), name='account_detail'),
    path('category/create/', views.CategoryCreate.as_view(), name='category_create'),
    path('transaction/create/', views.TransactionCreate.as_view(), name='transaction_create'),
]
