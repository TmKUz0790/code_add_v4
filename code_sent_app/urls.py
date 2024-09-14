from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_login, name='login'),
    path('select-choice/', views.select_choice, name='select_choice'),
    path('send-serial-numbers/', views.send_serial_numbers, name='send_serial_numbers'),
    path('choice-serial/', views.choice_serial_view, name='choice_serial_view'),
]
