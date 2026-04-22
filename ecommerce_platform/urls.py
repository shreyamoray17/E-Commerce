from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger configuration
schema_view = get_schema_view(
    openapi.Info(
        title="E-commerce API",
        default_version='v1',
        description="""
        A simple e-commerce platform with the following features:
        - JWT Authentication (Customer & Admin roles)
        - Product Management with Redis Caching
        - Shopping Cart
        - Order Management
        - Mock Payment Gateway
        
        ## Authentication
        Use the /api/auth/register/ endpoint to create an account.
        Then use /api/auth/login/ to get your JWT tokens.
        Click 'Authorize' button and enter: Bearer <your_access_token>
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@ecommerce.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # All API endpoints
    path('api/', include('urls.api')),
    
    # Swagger/OpenAPI documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='api-root'),
]
