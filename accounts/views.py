from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Merchant
from .serializers import MerchantSerializer

class RegisterView(generics.CreateAPIView):
    queryset = Merchant.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = MerchantSerializer
