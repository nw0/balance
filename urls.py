from django.urls import path

from . import views

app_name = 'balance'
urlpatterns = [
    path('dashboard/', views.AccountList.as_view(), name='account_list'),
    path('account/create/', views.AccountCreate.as_view(), name='account_create'),
    path('account/<int:pk>/', views.account_redirect, name='account_detail'),
    path('account/<int:account_pk>/<int:year>/<int:month>/', views.AccountMonth.as_view(month_format='%m'), name='account_month'),
    path('balance/update/', views.BalanceUpdate.as_view(), name='balance_update'),

    path('category/', views.CategoryList.as_view(), name='category_list'),
    path('category/<int:pk>/', views.category_redirect, name='category_detail'),
    path('category/<int:category_pk>/<int:year>/<int:month>/', views.CategoryMonth.as_view(month_format='%m'), name='category_month'),
    path('category/create/', views.CategoryCreate.as_view(), name='category_create'),

    path('transaction/<int:pk>/', views.TransactionDetail.as_view(), name='transaction_detail'),
    path('transaction/create/', views.TransactionCreate.as_view(), name='transaction_create'),
    path('transaction/<int:pk>/update/', views.TransactionUpdate.as_view(), name='transaction_update'),
    path('transaction/<int:pk>/delete/', views.TransactionDelete.as_view(), name='transaction_delete'),

    path('budget/', views.BudgetList.as_view(), name='budget_list'),
    path('budget/<int:pk>/', views.BudgetDetail.as_view(), name='budget_detail'),
    path('budget/create/', views.BudgetCreate.as_view(), name='budget_create'),

    path('budget/<int:budget_pk>/allocate/', views.AllocationCreate.as_view(), name='allocation_create'),
]
