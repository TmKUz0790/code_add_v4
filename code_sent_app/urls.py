# serial_sender/urls.py

from django.urls import path
from .views import send_serial_numbers, CustomLoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('send-serial-numbers/', send_serial_numbers, name='send_serial_numbers'),
    path('', CustomLoginView.as_view(), name='login'),
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
