from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from shops.auth import CustomerJWTAuthentication
from .models import Cart, CartItem, Order, OrderItem, Address
from .serializers import CartSerializer, OrderSerializer
from products.models import Product

class CartView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, shop_slug):
        if request.user.shop.slug != shop_slug:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        cart, created = Cart.objects.get_or_create(customer=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CartItemView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, shop_slug):
        if request.user.shop.slug != shop_slug:
            return Response(status=status.HTTP_403_FORBIDDEN)

        cart, _ = Cart.objects.get_or_create(customer=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id, shop=request.user.shop)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response(CartSerializer(cart).data)

    def patch(self, request, shop_slug, item_id):
        if request.user.shop.slug != shop_slug:
            return Response(status=status.HTTP_403_FORBIDDEN)

        cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
        quantity = int(request.data.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        return Response(CartSerializer(cart_item.cart).data)

    def delete(self, request, shop_slug, item_id):
        if request.user.shop.slug != shop_slug:
            return Response(status=status.HTTP_403_FORBIDDEN)

        cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
        cart = cart_item.cart
        cart_item.delete()

        return Response(CartSerializer(cart).data)

class CheckoutView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, shop_slug):
        if request.user.shop.slug != shop_slug:
            return Response(status=status.HTTP_403_FORBIDDEN)

        customer = request.user
        try:
            cart = Cart.objects.get(customer=customer)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        address_data = request.data.get('address')
        payment_method = request.data.get('payment_method', 'Cash on Delivery')

        if not address_data:
            return Response({'error': 'Address is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Create or use existing address
        address_id = address_data.get('id')
        if address_id:
            address = get_object_or_404(Address, id=address_id, customer=customer)
        else:
            address = Address.objects.create(
                customer=customer,
                street=address_data.get('street', ''),
                city=address_data.get('city', ''),
                state=address_data.get('state', ''),
                zip_code=address_data.get('zip_code', ''),
                is_default=True
            )

        total_amount = sum(item.product.price * item.quantity for item in cart.items.all())

        order = Order.objects.create(
            shop=customer.shop,
            customer=customer,
            address=address,
            payment_method=payment_method,
            total_amount=total_amount,
            status='PAID' if payment_method != 'Cash on Delivery' else 'PENDING'
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                price=cart_item.product.price,
                quantity=cart_item.quantity
            )
            # Deduct inventory
            if cart_item.product.inventory_count >= cart_item.quantity:
                cart_item.product.inventory_count -= cart_item.quantity
                cart_item.product.save()

        # Clear cart
        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class OrderListView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, shop_slug):
        if request.user.shop.slug != shop_slug:
            return Response(status=status.HTTP_403_FORBIDDEN)

        orders = Order.objects.filter(customer=request.user).order_by('-created_at')
        return Response(OrderSerializer(orders, many=True).data)
