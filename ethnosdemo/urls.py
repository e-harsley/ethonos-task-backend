"""
URL configuration for ethnosdemo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from ninja import NinjaAPI
from accounts.api import router as accounts_router
from wallet.api import router as wallet_router

# Initialize Ninja API
api = NinjaAPI(
    title="Deji's Wallet API",
    version="1.0.0",
    description="A comprehensive wallet application API for managing finances, cards, and transactions"
)

# Register routers
api.add_router("/auth", accounts_router, tags=["Authentication"])
api.add_router("/wallet", wallet_router, tags=["Wallet"])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
