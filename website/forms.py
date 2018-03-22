from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit

from website.models import Person, Import

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
                Div('year', css_class='col-6'),
                Div('year_actual', css_class='col-6'),
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


class ImportCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImportCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('cemetery', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('file', css_class='col-6'),
                css_class='row'
            ),
            Submit('submit', 'Импортировать', css_class='btn btn-primary'),
        )

    class Meta:
        model = Import
        fields = ['file', 'cemetery']


class ImportUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImportUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('cemetery', css_class='col-md-6'),
                css_class='row'
            ),
            Div(
                Div('header', css_class='col-md-6'),
                Div('numbering', css_class='col-md-6'),
                css_class='row'
            ),
            Div(
                Div('delimiter', css_class='col-md-6'),
                Div('quotechar', css_class='col-md-6'),
                css_class='row'
            ),
            Submit('submit', 'Применить', css_class='btn btn-primary'),
        )

    class Meta:
        model = Import
        fields = ['cemetery', 'header', 'numbering', 'delimiter', 'quotechar']


class ImportDoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        columns_count = kwargs.pop('columns_count', 0)
        super(ImportDoForm, self).__init__(*args, **kwargs)

        mapped_fields = Person.get_mapped_fields()
        mapping = []
        for field in mapped_fields:
            mapping.append((field, Person._meta.get_field(field).verbose_name))

        for column in range(columns_count):
            field_name = 'column_%s' % column
            self.fields[field_name] = forms.ChoiceField(required=False, choices=mapping)
