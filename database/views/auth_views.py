from django.http import HttpRequest, HttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def user_login(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Проверка на существование пользователя и его статус
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                return render(request, 'database/login.html',
                              {'error': 'Ваша учетная запись деактивирована, обратитесь к администрации.'})
        except User.DoesNotExist:
            pass

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('user_applications')
        else:
            return render(request, 'database/login.html', {'error': 'Неправильный логин или пароль'})
    else:
        return render(request, 'database/login.html')
