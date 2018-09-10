from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit, Button, HTML, ButtonHolder

from website.models import Person, Import, Hospital, Cemetery

from django.utils.translation import ugettext_lazy as _


class PersonCreateEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PersonCreateEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = True

        fields = Person.get_pair_card_fields()
        layout = Layout()
        self.fields['ontombstone'].widget.attrs['tabindex'] = 1
        self.fields['ontombstone'].widget.attrs['autofocus'] = 1
        self.fields['ontombstone'].widget.attrs['style'] = "text-transform:capitalize"
        self.fields['fio'].widget.attrs['style'] = "text-transform:capitalize"
        self.fields['fio_actual'].widget.attrs['style'] = "text-transform:capitalize"

        layout.append(Div(Div('ontombstone', css_class='col-12'), css_class='row'))

        layout.append(
            Div(
                Div(HTML("<b>Первичные данные</b>"), css_class='col text-center'),
                Div(HTML("<b>Актуальные данные</b>"), css_class='col text-center'),
                css_class='row')
        )

        i = 0
        for f, f_actual in fields:
            self.fields[f].widget.attrs['tabindex'] = 2
            self.fields[f].label = False
            self.fields[f_actual].widget.attrs['tabindex'] = 5
            self.fields[f_actual].label = False
            label = Person._meta.get_field(f).verbose_name
            row_color = '' if i % 2 else ' bg-light'
            layout.append(
                Div(
                    Div(HTML("<label>{0}</label>".format(label)), css_class="col"),
                    css_class='row pt-2' + row_color
                )
            )
            layout.append(
                Div(
                    Div(f, css_class='col'),
                    Div(
                        Button('copy', "=>", css_class='btn',  onclick="javascript:copy_data('id_{0}','id_{1}')".format(f, f_actual)),
                        css_class='col-md-auto'
                    ),
                    Div(f_actual, css_class='col'),
                    css_class='row' + row_color)
            )
            i += 1

        self.fields['notes'].widget.attrs['tabindex'] = 3
        layout.append(Div(Div('notes', css_class='col-12'), css_class='row'))
        layout.append(Submit('submit', _('Сохранить'), css_class='btn btn-primary', tabindex=4))
        self.helper.layout = layout

    class Meta:
        model = Person
        exclude = ['active_import']


class ImportCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImportCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('file', css_class='col-6'),
                css_class='row'
            ),
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
            Submit('submit', 'Сохранить', css_class='btn btn-primary'),
        )

    class Meta:
        model = Import
        fields = ['cemetery', 'file', 'header', 'numbering', 'delimiter', 'quotechar']


class ImportEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImportEditForm, self).__init__(*args, **kwargs)
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
            Submit('submit', 'Сохранить', css_class='btn btn-primary'),
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


class HospitalCreateEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HospitalCreateEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-6'),
                css_class='row'
            ),
            Submit('submit', 'Сохранить', css_class='btn btn-primary'),
        )

    class Meta:
        model = Hospital
        fields = ['name']


class CemeteryCreateEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CemeteryCreateEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-6'),
                css_class='row'
            ),
            Submit('submit', 'Сохранить', css_class='btn btn-primary'),
        )

    class Meta:
        model = Cemetery
        fields = ['name']


class PersonSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PersonSearchForm, self).__init__(*args, **kwargs)

        self.fields['fio'] = forms.CharField(required=False)
        self.fields['fio'].label = 'ФИО'

        self.fields['born_year'] = forms.CharField(required=False)
        self.fields['born_year'].label = 'Год рождения'

        self.helper = FormHelper()
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            Div('fio'),
            Div('born_year'),
            ButtonHolder(
                Submit('submit', 'Искать', css_class='btn btn-primary'),
                Button('copy', "Сброс", css_class='btn', onclick="javascript:reset_search()"),
            )
        )
