from django.urls import path

from . import views

app_name = 'balance'
urlpatterns = [
    path('', views.AccountList.as_view(), name='account_list'),
    path('account/create/', views.AccountCreate.as_view(), name='account_create'),
    path('account/<int:pk>/', views.AccountDetail.as_view(), name='account_detail'),
    path('balance/update/', views.BalanceUpdate.as_view(), name='balance_update'),
    path('category/', views.CategoryList.as_view(), name='category_list'),
    path('category/<int:pk>/', views.category_redirect, name='category_detail'),
    path('category/<int:category_pk>/<int:year>/<int:month>/', views.CategoryMonth.as_view(month_format='%m'), name='category_month'),
    path('category/create/', views.CategoryCreate.as_view(), name='category_create'),
    path('transaction/create/', views.TransactionCreate.as_view(), name='transaction_create'),
]
