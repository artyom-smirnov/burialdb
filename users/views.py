from django.contrib.auth.views import LoginView
from users.forms import ReCaptchaAuthenticationForm
from django.shortcuts import render


class ReCaptchaLoginView(LoginView):
    form_class = ReCaptchaAuthenticationForm
