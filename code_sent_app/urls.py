# serial_sender/urls.py

from django.urls import path
from .views import send_serial_numbers,CustomLoginView,home
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('send-serial-numbers/', send_serial_numbers, name='send_serial_numbers'),
    path('home/', home, name='home'),
    path('', CustomLoginView.as_view(), name='login'),

]
