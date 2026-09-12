from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def home(request):
    return render(request, 'attendance/home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        return render(
            request,
            'attendance/login.html',
            {'error': 'Invalid username or password.'}
        )

    return render(request, 'attendance/login.html')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'attendance/dashboard.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)

    return redirect('home')