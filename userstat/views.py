from django.shortcuts import render
from rest_framework.views import APIView
from datetime import date, datetime, timedelta
from expenses.models import Expense
from income.models import Income
from rest_framework import response,status

class ExpenseSummaryStat(APIView):

    def get_expense_amount(self,expense_list, category):
        expenses = expense_list.filter(category=category)
        amount = 0

        for expense in expenses:
            amount += expense.amount

        return {'amount':str(amount)}

    def get_category(self, expense):
        return expense.category

    def get(self, request):
        todays_date = datetime.today()
        a_year_ago = todays_date-timedelta(30*12)
        expenses = Expense.objects.filter(
            owner=request.user,
            date__gte=a_year_ago,
            date__lte=todays_date
        )

        final = {}
        categories = list(set(map(self.get_category, expenses)))

        for expense in expenses:
            for category in categories:
                final[category] = self.get_expense_amount(expenses, category)

        return response.Response({'category_data':final},status=status.HTTP_200_OK)


class IncomeSourcesSummaryStat(APIView):

    def get_income_amount(self,income_list, source):
        incomes = income_list.filter(source=source)
        amount = 0

        for income in incomes:
            amount += income.amount

        return {'amount':str(amount)}

    def get_source(self, income):
        return income.source

    def get(self, request):
        todays_date = datetime.today()
        a_year_ago = todays_date-timedelta(30*12)
        incomes = Income.objects.filter(
            owner=request.user,
            date__gte=a_year_ago,
            date__lte=todays_date
        )

        final = {}
        sources = list(set(map(self.get_source, incomes)))

        for income in incomes:
            for source in sources:
                final[source] = self.get_income_amount(incomes, source)

        return response.Response({'source_data':final},status=status.HTTP_200_OK)