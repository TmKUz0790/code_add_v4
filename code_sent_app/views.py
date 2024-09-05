from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django import forms
import asyncio
import aiohttp
from django.views.decorators.csrf import csrf_protect
from .models import UserChoice
from asgiref.sync import sync_to_async


class ChoiceForm(forms.Form):
    OPTION_CHOICES = [
        ('01-filial', '01-filial'),
        ('06-filial', '06-filial'),
        ('07-filial', '07-filial'),
        ('08-filial', '08-filial'),
        ('11-filial', '11-filial'),
        ('12-filial', '12-filial'),
        ('Akfa Savdo Markazi', 'Akfa Savdo Markazi'),
        ('Chirchiq', 'Chirchiq'),
        ('Farid O`rikzor', 'Farid O`rikzor'),
        ('Gulistan', 'Gulistan'),
        ('Olmaliq', 'Olmaliq'),
        ('Qo\'yliq showroom', 'Qo\'yliq showroom'),
        ('Sherali Gvardeyskiy', 'Sherali Gvardeyskiy'),
        ('TIYA showroom', 'TIYA showroom'),
        ('Reklama do\'kon', 'Reklama do\'kon'),
        ('Namangan baza','Namangan baza'),
        ('Namangan I Yusufxon Aka', 'Namangan I Yusufxon Aka'),
        ('Namangan II Yusufxon Aka', 'Namangan II Yusufxon Aka'),
        ('Fargona I Sherzod aka', 'Fargona I Sherzod aka'),
        ('Fargona II Shuxrat Aka', 'Fargona II Shuxrat Aka'),
        ('Andijon I Murodxon Aka', 'Andijon I Murodxon Aka'),
        ('Shaxrixon Bobur Aka', 'Shaxrixon Bobur Aka'),
        ('Qo\'qon Shuxrat+Jahongir', 'Qo\'qon Shuxrat+Jahongir'),
        ('Samarqand baza', 'Samarqand baza'),
        ('Samarqand-1 Akmal Aka', 'Samarqand-1 Akmal Aka'),
        ('Samarqand-2 Umid Aka', 'Samarqand-2 Umid Aka'),
        ('Asqar Jizzax', 'Asqar Jizzax'),
        ('Kitob Xamza Aka', 'Kitob Xamza Aka'),
        ('OPT. Sardor Qarshi', 'OPT. Sardor Qarshi'),
        ('Surxandaryo Azamat Aka', 'Surxandaryo Azamat Aka'),
        ('OPT. Ortiq Termez', 'OPT. Ortiq Termez'),
        ('OPT. Anvar Denov', 'OPT. Anvar Denov'),
        ('Buxoro baza', 'Buxoro baza'),
        ('G\'ijduvon Mironshox', 'G\'ijduvon Mironshox'),
        ('Romitan Ulug\'bek Aka', 'Romitan Ulug\'bek Aka'),
        ('OPT. Botir Buxoro', 'OPT. Botir Buxoro'),
        ('Ulug\'bek Buxoro', 'Ulug\'bek Buxoro'),
        ('Navoiy-2 Botir Aka', 'Navoiy-2 Botir Aka'),
        ('Navoiy Mironshox', 'Navoiy Mironshox'),
        ('Navoiy Qaxramon', 'Navoiy Qaxramon'),
        ('Xorazm baza', 'Xorazm baza'),
        ('Xorazm 2 Egamberdi Aka', 'Xorazm 2 Egamberdi Aka'),
        ('Turtkul Umid Aka', 'Turtkul Umid Aka'),
        ('Nukus Davlat', 'Nukus Davlat'),
        ('OPT. Marimboy Aka', 'OPT. Marimboy Aka'),
    ]

    choice = forms.ChoiceField(choices=OPTION_CHOICES, widget=forms.RadioSelect)


@csrf_protect
async def my_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Using sync_to_async to wrap synchronous authentication
        user = await sync_to_async(authenticate)(username=username, password=password)

        if user is not None:
            await sync_to_async(login)(request, user)
            return redirect('select_choice')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password.'})

    return render(request, 'login.html')


@login_required
async def select_choice(request):
    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            request.session['user_choice'] = form.cleaned_data['choice']
            return redirect('send_serial_numbers')
    else:
        form = ChoiceForm()
    return render(request, 'select_choice.html', {'form': form})


from asgiref.sync import sync_to_async

@login_required
async def send_serial_numbers(request):
    user_email = await sync_to_async(lambda: request.user.email)()
    if user_email not in ['admin_tmk@gmail.com', 'tmk5775@gmail.com']:
        return render(request, 'send_serial_numbers.html', {
            'error': 'You do not have permission to send serial numbers. Please contact us to get access: +998 97 776 22 07'
        })

    if request.method == 'POST':
        serial_numbers = request.POST.get('serial_numbers')
        serial_numbers_list = [s.strip() for s in serial_numbers.split(',') if s.strip()]

        user_choice = request.session.get('user_choice')

        if user_choice and serial_numbers_list:
            result = await send_codes_async(serial_numbers_list)

            # Saving both successful and failed serial numbers to the database
            all_serials = [UserChoice(choice=user_choice, serial_number=serial) for serial in serial_numbers_list]
            await sync_to_async(UserChoice.objects.bulk_create)(all_serials)

            success_count = len(result['successful'])
            failed_count = len(result['failed'])

            context = {}
            if success_count:
                context['success'] = f'Yuborildi  {success_count} code.'
            if failed_count:
                context['error'] = f'Mavjud kodlar {failed_count} .'

            return render(request, 'send_serial_numbers.html', context)

        return render(request, 'send_serial_numbers.html', {
            'error': 'Iltimos kodni kiriting'
        })

    return render(request, 'send_serial_numbers.html')

async def send_codes_async(serial_numbers):
    url = 'https://api.akfacomfort.uz/services/admin/api/codes/akfa-code'
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
        tasks = [send_code(session, url, number) for number in serial_numbers]
        responses = await asyncio.gather(*tasks)
        failed_serials = [num for res, num in zip(responses, serial_numbers) if res != 200]
        successful_serials = [num for res, num in zip(responses, serial_numbers) if res == 200]
        return {'successful': successful_serials, 'failed': failed_serials}

async def send_code(session, url, serial_number):
    payload = {'serialNumber': serial_number}
    try:
        async with session.post(url, json=payload) as response:
            return response.status
    except Exception:
        return 500

async def send_code(session, url, serial_number):
    payload = {'serialNumber': serial_number}
    try:
        async with session.post(url, json=payload) as response:
            return response.status
    except Exception:
        return 500


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=254)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            # Fetch the user synchronously because this is a synchronous method
            self.user_cache = User.objects.filter(email=email).first()
            if not self.user_cache or not self.user_cache.check_password(password):
                raise forms.ValidationError("Invalid email or password.")
        return self.cleaned_data


class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = EmailAuthenticationForm

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect('select_choice')
