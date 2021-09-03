from django.shortcuts import render
from .models import Expense
from .serializers import ExpenseSerializer
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner

class ExpenseListApiView(ListCreateAPIView):

    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)



class ExpenseDetailApiView(RetrieveUpdateDestroyAPIView):

    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()
    permission_classes = (IsAuthenticated,IsOwner,)
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)