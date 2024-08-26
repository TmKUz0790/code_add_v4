from django.contrib.auth import login, authenticate
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
import requests
from django.views.decorators.csrf import csrf_protect


@login_required
def send_serial_numbers(request):
    if request.user.email != 'tmk5775@gmail.com':
        return render(request, 'send_serial_numbers.html', {'error': 'Sizda ruxsat mavjud emas ruxsat olish uchun biz '
                                                                     'bilan boglaning: +998 97 776 22 07'})

    if request.method == 'POST':
        serial_numbers = request.POST.get('serial_numbers')
        # Split the input by commas and strip any extra whitespace from each serial number
        serial_numbers_list = [s.strip() for s in serial_numbers.split(',') if s.strip()]
        failed_serials = []

        url = 'https://api.akfacomfort.uz/services/admin/api/codes/akfa-code'

        for serial_number in serial_numbers_list:
            payload = {'serialNumber': serial_number}
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                failed_serials.append(serial_number)

        if failed_serials:
            error_message = f"Bu kodlar yuborilmadi sabab ular allaqachon majvud yoki xato kiritilgan : {', '.join(failed_serials)}"
            return render(request, 'send_serial_numbers.html', {'error': error_message})
        else:
            success_message = "Barcha kodlar muvaffaqiyatli yuborildi."
            return render(request, 'send_serial_numbers.html', {'success': success_message})

    return render(request, 'send_serial_numbers.html')


@csrf_protect
def my_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if user.email == 'admin_tmk@gmail.com':
                return redirect('send_serial_numbers')
            elif user.email == 'tmk5775@gmail.com':
                return redirect('send_serial_numbers')


        else:
            return render(request, 'login.html', {'error': 'Invalid username or password.'})

    return render(request, 'login.html')


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=254)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = User.objects.filter(email=email).first()
            if not self.user_cache:
                raise forms.ValidationError("Invalid email or password.")
            if not self.user_cache.check_password(password):
                raise forms.ValidationError("Invalid email or password.")

        return self.cleaned_data


from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    return render(request, 'home.html')


class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = EmailAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        if user.email == 'admin_tmk@gmail.com':
            return redirect('send_serial_numbers')
        elif user.email == 'tmk5775@gmail.com':
            return redirect('send_serial_numbers')
        else:
            # Redirect to a default home page or another appropriate page
            return redirect('home')
