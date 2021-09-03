from .models import Income
from .serializers import IncomeSerializer
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner

class IncomeListApiView(ListCreateAPIView):

    serializer_class = IncomeSerializer
    queryset = Income.objects.all()
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)



class IncomeDetailApiView(RetrieveUpdateDestroyAPIView):

    serializer_class = IncomeSerializer
    queryset = Income.objects.all()
    permission_classes = (IsAuthenticated,IsOwner,)
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)