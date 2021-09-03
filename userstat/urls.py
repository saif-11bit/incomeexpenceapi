from django.urls import path
from .views import ExpenseSummaryStat,IncomeSourcesSummaryStat


urlpatterns = [
    path('expense-category-data/', ExpenseSummaryStat.as_view(), name='expense-category-data'),
    path('income-source-data/', IncomeSourcesSummaryStat.as_view(), name='income-source-data'),
]

