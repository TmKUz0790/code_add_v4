from django.urls import path
from .views import my_login, select_choice, send_serial_numbers, CustomLoginView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('select_choice/', select_choice, name='select_choice'),
    path('send_serial_numbers/', send_serial_numbers, name='send_serial_numbers'),
]
