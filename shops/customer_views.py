from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Shop, Customer
from .auth import CustomerJWTAuthentication, generate_customer_token
from orders.models import Address

class CustomerRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, shop_slug):
        try:
            shop = Shop.objects.get(slug=shop_slug)
        except Shop.DoesNotExist:
            return Response({'error': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)

        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name')

        if not email or not password or not name:
            return Response({'error': 'Email, password, and name are required'}, status=status.HTTP_400_BAD_REQUEST)

        if Customer.objects.filter(shop=shop, email=email).exists():
            return Response({'error': 'Email already registered in this shop'}, status=status.HTTP_400_BAD_REQUEST)

        customer = Customer(shop=shop, email=email, name=name)
        customer.set_password(password)
        customer.save()

        token = generate_customer_token(customer)
        return Response({
            'token': token,
            'customer': {
                'id': customer.id,
                'email': customer.email,
                'name': customer.name
            }
        }, status=status.HTTP_201_CREATED)

class CustomerLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, shop_slug):
        try:
            shop = Shop.objects.get(slug=shop_slug)
        except Shop.DoesNotExist:
            return Response({'error': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)

        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(shop=shop, email=email)
        except Customer.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not customer.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        token = generate_customer_token(customer)
        return Response({
            'token': token,
            'customer': {
                'id': customer.id,
                'email': customer.email,
                'name': customer.name
            }
        }, status=status.HTTP_200_OK)

class CustomerMeView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, shop_slug):
        # We need to make sure the customer belongs to the shop
        customer = request.user
        if customer.shop.slug != shop_slug:
            return Response({'error': 'Unauthorized for this shop'}, status=status.HTTP_401_UNAUTHORIZED)

        addresses = Address.objects.filter(customer=customer)
        address_data = [{
            'id': a.id,
            'street': a.street,
            'city': a.city,
            'state': a.state,
            'zip_code': a.zip_code,
            'is_default': a.is_default
        } for a in addresses]

        return Response({
            'id': customer.id,
            'email': customer.email,
            'name': customer.name,
            'addresses': address_data
        })
