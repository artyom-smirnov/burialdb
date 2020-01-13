from captcha.fields import ReCaptchaField
from django.contrib.auth.forms import AuthenticationForm


class ReCaptchaAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField()
