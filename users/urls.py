from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings

from users.views import ReCaptchaLoginView

use_captcha = settings.RECAPTCHA_ENABLED

urlpatterns = [
    path('login/', ReCaptchaLoginView.as_view() if use_captcha else auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),
]
