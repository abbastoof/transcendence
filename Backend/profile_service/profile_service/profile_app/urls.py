from django.contrib import admin
from django.urls import path, include
from .views import UserSessionViewClass

urlpatterns = [
    path('login/', UserSessionViewClass.as_view({'post': 'login'}), name="login"),
    path('logout/', UserSessionViewClass.as_view({'post': 'logout'}), name="logout"),
]
