from django.urls import path
from .views import ExpenseListApiView,ExpenseDetailApiView


urlpatterns = [
    path('', ExpenseListApiView.as_view(),name='expenses'),
    path('<int:id>/', ExpenseDetailApiView.as_view(),name='expense-detail'),
]