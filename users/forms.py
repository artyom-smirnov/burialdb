from django.contrib.auth.forms import AuthenticationForm
from snowpenguin.django.recaptcha3.fields import ReCaptchaField


class ReCaptchaAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField()
