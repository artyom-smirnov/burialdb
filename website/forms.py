from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit, Button, HTML, ButtonHolder, Hidden

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
        layout.append(Div(Div('state', css_class='col-12'), css_class='row'))

        layout.append(
            Div(
                Div(HTML("<b>Первичные данные</b>"), css_class='col text-center'),
                Div(HTML("<b>Актуальные данные</b>"), css_class='col text-center'),
                css_class='row')
        )

        i = 0
        for f, f_actual in fields:
            additional_classes = ''
            if f in Person._hide_if_treated:
                additional_classes += ' hide-if-treated'
            if f in Person._hide_if_mia:
                additional_classes += ' hide-if-mia'
            if f in Person._hide_if_killed:
                additional_classes += ' hide-if-killed'
            if f in Person._hide_if_dead_in_road:
                additional_classes += ' hide-if-deadinroad'
            if f in Person._hide_if_dead_in_captivity:
                additional_classes += ' hide-if-deadincaptivity'

            self.fields[f].widget.attrs['tabindex'] = 2
            self.fields[f].label = False
            self.fields[f_actual].widget.attrs['tabindex'] = 5
            self.fields[f_actual].label = False
            label = Person._meta.get_field(f).verbose_name
            row_color = '' if i % 2 else ' bg-light'
            layout.append(
                Div(
                    Div(HTML("<label>{0}</label>".format(label)), css_class="col"),
                    css_class='row pt-2' + row_color + additional_classes
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
                    css_class='row' + row_color + additional_classes)
            )
            i += 1

        self.fields['notes'].widget.attrs['tabindex'] = 3
        layout.append(Div(Div('notes', css_class='col-12'), css_class='row'))
        layout.append(Div(Submit('submit', _('Сохранить'), css_class='btn btn-primary', tabindex=4), css_class='fixed-submit-button'))
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

        fields = (
            ('fio', forms.CharField(required=False), 'ФИО'),
            ('born_year', forms.CharField(required=False), 'Год рождения'),
            # -1 value - hack for searching rows with is null, see views.PersonsView.get_queryset
            ('state', forms.ChoiceField(choices=((None, ''), (-1, 'Без категории')) + Person.STATES, required=False), 'Категория'),
            ('cemetery', forms.CharField(required=False), 'Захоронение'),
            ('hospital', forms.CharField(required=False), 'Госпиталь'),
            ('born_region', forms.CharField(required=False), 'Регион (страна) рождения'),
            ('born_address', forms.CharField(required=False), 'Адрес рождения'),
            ('conscription_place', forms.CharField(required=False), 'Место призыва'),
            ('military_unit', forms.CharField(required=False), 'Часть'),
            ('rank', forms.CharField(required=False), 'Звание'),
            ('position', forms.CharField(required=False), 'Должность'),
            ('address', forms.CharField(required=False), 'Место жительства'),
            ('relatives', forms.CharField(required=False), 'Родственники'),
            ('receipt_date', forms.CharField(required=False), 'Дата поступления'),
            ('receipt_cause', forms.CharField(required=False), 'Причина поступления'),
            ('death_date', forms.CharField(required=False), 'Дата смерти'),
            ('death_cause', forms.CharField(required=False), 'Причина смерти'),
            ('grave', forms.CharField(required=False), 'Расположение могилы'),
            ('date_of_captivity', forms.CharField(required=False), 'Дата пленения'),
            ('place_of_captivity', forms.CharField(required=False), 'Место пленения'),
            ('camp', forms.CharField(required=False), 'Лагерь'),
            ('camp_number', forms.CharField(required=False), 'Лагерный номер'),
            ('lost_date', forms.CharField(required=False), 'Связь прекращена'),
            ('field_post', forms.CharField(required=False), 'Полевая почта'),
            ('notes', forms.CharField(required=False), 'Примечания'),
            ('advanced_search', forms.IntegerField(widget=forms.HiddenInput(), initial=0), '')
        )

        for f in fields:
            self.fields[f[0]] = f[1]
            self.fields[f[0]].label = f[2]

        self.helper = FormHelper()

        self.helper.layout = Layout(
            Div(
                Div('fio', css_class='col-md-4'),
                Div('born_year', css_class='col-md-4'),
                Div('state', css_class='col-md-4'),
                css_class='row'
            ),

            Div(
                Div('cemetery', css_class='col-md-4'),
                Div('hospital', css_class='col-md-4'),
                Div('born_region', css_class='col-md-4'),
                Div('born_address', css_class='col-md-4'),
                Div('conscription_place', css_class='col-md-4'),
                Div('military_unit', css_class='col-md-4'),
                Div('rank', css_class='col-md-4'),
                Div('position', css_class='col-md-4'),
                Div('address', css_class='col-md-4'),
                Div('relatives', css_class='col-md-4'),
                Div('receipt_date', css_class='col-md-4'),
                Div('receipt_cause', css_class='col-md-4'),
                Div('death_date', css_class='col-md-4'),
                Div('death_cause', css_class='col-md-4'),
                Div('grave', css_class='col-md-4'),
                Div('date_of_captivity', css_class='col-md-4'),
                Div('place_of_captivity', css_class='col-md-4'),
                Div('camp', css_class='col-md-4'),
                Div('camp_number', css_class='col-md-4'),
                Div('lost_date', css_class='col-md-4'),
                Div('field_post', css_class='col-md-4'),
                Div('notes', css_class='col-md-4'),
                css_class='row d-none', css_id='advanced-search-fields'
            ),

            Div(
                Button('advanced_search_on_btn', "Расширенный поиск", css_class='btn', css_id='advanced-search-on', onclick="javascript:advanced_search_on()"),
                Button('advanced_search_off_btn', "Обычный поиск", css_class='btn d-none', css_id='advanced-search-off', onclick="javascript:advanced_search_off()"),
            ),

            'advanced_search',

            ButtonHolder(
                Submit('submit', 'Искать', css_class='btn btn-primary'),
                Button('reset', "Сброс", css_class='btn', onclick="javascript:reset_search()"),
                css_class='mt-3'
            )
        )
