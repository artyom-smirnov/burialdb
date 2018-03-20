from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit

from website.models import Person

from django.utils.translation import ugettext_lazy as _


class PersonCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PersonCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = True
        self.helper.layout = Layout(
            Div(
                Div('fio', css_class='col-6'),
                Div('fio_actual', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('hospital', css_class='col-6'),
                Div('hospital_actual', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('cemetery', css_class='col-6'),
                Div('cemetery_actual', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('notes', css_class='col-12'),
                css_class='row'
            ),
            Submit('submit', _('Сохранить'), css_class='btn btn-primary'),
        )

    class Meta:
        model = Person
        fields = '__all__'
