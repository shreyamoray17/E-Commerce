from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from views import users, products, orders, payments

# Router for Product ViewSet
router = DefaultRouter()
router.register(r'products', products.ProductViewSet, basename='product')

urlpatterns = [
    # AUTHENTICATION ENDPOINTS
    path('auth/register/', users.RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', users.logout_view, name='logout'),
    path('auth/profile/', users.get_user_profile, name='profile'),
    path('auth/profile/update/', users.update_user_profile, name='profile_update'),
    
    # CART ENDPOINTS
    path('cart/', orders.get_cart, name='cart'),
    path('cart/add/', orders.add_to_cart, name='cart_add'),
    path('cart/update/<int:item_id>/', orders.update_cart_item, name='cart_update'),
    path('cart/remove/<int:item_id>/', orders.remove_from_cart, name='cart_remove'),
    
    # ORDER ENDPOINTS
    path('orders/', orders.list_orders, name='order_list'),
    path('orders/create/', orders.create_order, name='order_create'),
    path('orders/<int:order_id>/', orders.get_order, name='order_detail'),
    
    # PAYMENT ENDPOINTS
    path('payments/initiate/', payments.initiate_payment, name='payment_initiate'),
    path('payments/status/<int:order_id>/', payments.get_payment_status, name='payment_status'),
    path('payments/simulate-failure/', payments.simulate_payment_failure, name='payment_simulate_failure'),
]

# Add product router URLs
urlpatterns += router.urls
