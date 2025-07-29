from django.contrib.auth import get_user_model, login
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView

from users.backends import generate_username
from users.forms import RegisterForm


User = get_user_model()

def signup_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            potential_user_email = request.POST.get('email', False).lower()
            try:
                user = User.objects.get(email=potential_user_email)
                return render(request, 'registration/signup.html', {'error': 'Email has already been taken. Please try another'})
            except User.DoesNotExist:
                if form.is_valid():
                    new_user = User.objects.create_user(username=generate_username(),
                                                        email=potential_user_email,
                                                        password=request.POST['password1'])
                    login(request, new_user, backend='users.backends.EmailBackend')
                    return redirect('/accounts/login')
        else:
            return render(request, 'registration/signup.html', {'error': "Password's must match."})
    return render(request, 'registration/signup.html', {'form': form})