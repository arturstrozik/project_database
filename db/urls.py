"""db URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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

import database_project.views
from database_project import views as db_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', database_project.views.home),
    path('admin/', admin.site.urls),
    path('new_order/', database_project.views.new_order, name="new_order"),
    path('stock/', database_project.views.stock, name="stock"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("register/", db_views.register, name="register"),
    path("logout/", auth_views.logout_then_login, name="logout"),
    path("change_stock/", database_project.views.change_stock, name="change_stock")
]
