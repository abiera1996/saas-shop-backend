from django.urls import path, include
from shops.customer_views import CustomerRegisterView, CustomerLoginView, CustomerMeView
from .views import CartView, CartItemView, CheckoutView, OrderListView
from shops.views import StorefrontShopViewSet
from products.views import StorefrontProductViewSet

urlpatterns = [
    # Storefront Shop details & products
    path('<slug:slug>/', StorefrontShopViewSet.as_view({'get': 'retrieve'}), name='storefront-shop-detail'),
    path('<slug:shop_slug>/products/', StorefrontProductViewSet.as_view({'get': 'list'}), name='storefront-products'),
    path('<slug:shop_slug>/products/<int:pk>/', StorefrontProductViewSet.as_view({'get': 'retrieve'}), name='storefront-product-detail'),

    # Customer Auth
    path('<slug:shop_slug>/auth/register/', CustomerRegisterView.as_view(), name='customer-register'),
    path('<slug:shop_slug>/auth/login/', CustomerLoginView.as_view(), name='customer-login'),
    path('<slug:shop_slug>/auth/me/', CustomerMeView.as_view(), name='customer-me'),

    # Cart
    path('<slug:shop_slug>/cart/', CartView.as_view(), name='cart'),
    path('<slug:shop_slug>/cart/items/', CartItemView.as_view(), name='cart-items'),
    path('<slug:shop_slug>/cart/items/<int:item_id>/', CartItemView.as_view(), name='cart-item-detail'),

    # Orders & Checkout
    path('<slug:shop_slug>/checkout/', CheckoutView.as_view(), name='checkout'),
    path('<slug:shop_slug>/orders/', OrderListView.as_view(), name='orders'),
]
