from django.contrib.auth.forms import AuthenticationForm

from captcha.widgets import ReCaptchaV2Invisible
from captcha.fields import ReCaptchaField


class ReCaptchaAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField(label='', help_text='', widget=ReCaptchaV2Invisible)
