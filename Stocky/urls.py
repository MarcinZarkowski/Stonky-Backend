"""
URL configuration for Stocky project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include
from authuser.views import CreateUserView, validate_email_token,validate_reset_request, CustomTokenObtainPairView, csrf_token, change_password, search_stock, get_stock_pred, chat_with_RAG

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/register/', CreateUserView.as_view(), name="register"),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='refresh'),    
    path('api/validate-email-token/', validate_email_token ,name='validate_email_token'),
    path('api/request-password-change/',validate_reset_request, name='validate_reset_request'),
    path('api/password-change/', change_password, name="change_password"),
    path('api/csrf-token/', csrf_token, name='csrf_token'),
    path('api/stock-search/<str:query>/', search_stock, name='search_stock'),
    path('api/get-stock-pred/<str:ticker>/', get_stock_pred, name='get_stock_pred'),
    path('api/chat/', chat_with_RAG, name='chat_with_RAG'),
    path('api/', include('authuser.urls')),
    
]
