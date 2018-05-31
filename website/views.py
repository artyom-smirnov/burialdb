import csv
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.core import paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import BaseDetailView, SingleObjectMixin
from django.views.generic.edit import ProcessFormView, ModelFormMixin, BaseUpdateView, FormMixin
from django.db import transaction

from website.forms import PersonCreateEditForm, ImportCreateForm, ImportUpdateForm, ImportDoForm, HospitalCreateEditForm, \
    CemeteryCreateEditForm
from website.models import Person, Cemetery, Hospital, Import

from django.utils.translation import ugettext_lazy as _

PAGINATE_BY = 10


class CommonViewMixin(object):
    page_title = 'Untitled'
    navbar = None

    def get_page_title(self):
        return self.page_title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_page_title()
        context['navbar'] = self.navbar

        return context


class CommonPaginatedViewMixin(CommonViewMixin):
    paginate_by = PAGINATE_BY


class BaseListView(CommonPaginatedViewMixin, ListView):
    pass


class DetailWithListView(CommonPaginatedViewMixin, DetailView):
    list_model = None

    def get_list_queryset(self):
        return self.list_model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        request_page = self.request.GET.get("page")
        queryset = self.get_list_queryset()
        objects_paginator = paginator.Paginator(queryset, PAGINATE_BY)
        try:
            page = objects_paginator.page(request_page)
        except paginator.PageNotAnInteger:
            page = objects_paginator.page(1)
        except paginator.EmptyPage:
            if int(request_page) < 1:
                page = objects_paginator.page(1)
            else:
                page = objects_paginator.page(objects_paginator.num_pages)

        context['page_obj'] = page
        context['paginator'] = objects_paginator
        context['is_paginated'] = True if objects_paginator.num_pages > 1 else False
        return context


class CommonCreateEditView(CommonViewMixin, CreateView):
    template_name = 'website/common_create_edit.html'
    form_class = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CommonCreateEditView, self).dispatch(*args, **kwargs)


class CommonDeleteView(CommonViewMixin, DeleteView):
    model = None
    success_url = None
    navbar = None
    template_name = 'website/common_confirm_delete.html'

    def get_page_title(self):
        return 'Удаление ' + super().get_object().name()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CommonDeleteView, self).dispatch( *args, **kwargs)


class IndexView(TemplateView):
    template_name = "website/index.html"


class CemeteriesListView(BaseListView):
    model = Cemetery
    context_object_name = 'cemetery_list'
    page_title = 'Захоронения'
    navbar = 'burials'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CemeteriesListView, self).dispatch( *args, **kwargs)


class CemeteryDetailView(DetailWithListView):
    model = Cemetery
    list_model = Person
    context_object_name = 'cemetery'
    navbar = 'burials'

    def get_page_title(self):
        return 'Захоронение ' + super().get_object().name

    def get_list_queryset(self):
        obj = super().get_object()
        return Person.objects.filter(Q(active_import=None) & (Q(cemetery=obj) | Q(cemetery_actual=obj)))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CemeteryDetailView, self).dispatch( *args, **kwargs)


class CemeteryCreateView(CommonCreateEditView):
    model = Cemetery
    form_class = CemeteryCreateEditForm
    navbar = 'burials'
    page_title = 'Добавление нового захоронения'


class CemeteryEditView(CommonCreateEditView, UpdateView):
    model = Cemetery
    form_class = CemeteryCreateEditForm
    navbar = 'burials'
    page_title = 'Редактирование захоронения'

    def get_page_title(self):
        return 'Редактирование захоронения ' + super().get_object().name


class CemeteryDeleteView(CommonDeleteView):
    model = Cemetery
    success_url = reverse_lazy('cemeteries')
    navbar = 'burials'

    def get_page_title(self):
        return 'Удаление захоронения ' + super().get_object().name


class HospitalsView(BaseListView):
    model = Hospital
    context_object_name = 'hospital_list'
    page_title = 'Госпитали'
    navbar = 'hospitals'

    def get_queryset(self):
        return Hospital.objects.filter(active_import=None)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HospitalsView, self).dispatch( *args, **kwargs)


class HospitalDetailView(DetailWithListView):
    model = Hospital
    list_model = Person
    context_object_name = 'hospital'
    navbar = 'hospitals'

    def get_page_title(self):
        return 'Госпиталь ' + super().get_object().name

    def get_list_queryset(self):
        obj = super().get_object()
        return Person.objects.filter(Q(hospital=obj) | Q(hospital_actual=obj))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HospitalDetailView, self).dispatch( *args, **kwargs)


class HospitalCreateView(CommonCreateEditView):
    model = Hospital
    form_class = HospitalCreateEditForm
    navbar = 'hospitals'
    page_title = 'Добавление нового госпиталя'


class HospitalEditView(CommonCreateEditView, UpdateView):
    model = Hospital
    form_class = HospitalCreateEditForm
    navbar = 'hospitals'
    page_title = 'Редактирование госпиталя'

    def get_page_title(self):
        return 'Редактирование госпиталя ' + super().get_object().name


class HospitalDeleteView(CommonDeleteView):
    model = Hospital
    success_url = reverse_lazy('hospitals')
    navbar = 'hospitals'

    def get_page_title(self):
        return 'Удаление госпиталя ' + super().get_object().name


class PersonsView(BaseListView):
    model = Person
    context_object_name = 'person_list'
    navbar = 'persons'
    page_title = 'Люди'

    def get_queryset(self):
        return Person.objects.filter(active_import=None)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PersonsView, self).dispatch( *args, **kwargs)


class PersonDetailView(CommonViewMixin, DetailView):
    model = Person
    context_object_name = 'person'
    navbar = 'persons'

    def get_page_title(self):
        return super().get_object().name()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = super().get_object()
        person_card_pair_values = []
        for f, a_f in Person.get_pair_card_fields():
            caption = Person._meta.get_field(f).verbose_name
            val = getattr(person, f)
            a_val = getattr(person, a_f)
            person_card_pair_values.append(
                {'caption': caption, 'data': val, 'actual_data': a_val}
            )
        context['person_card_pair_values'] = person_card_pair_values
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PersonDetailView, self).dispatch( *args, **kwargs)


class PersonCreateView(CommonCreateEditView):
    model = Person
    form_class = PersonCreateEditForm
    navbar = 'persons'
    page_title = 'Добавление нового человека'


class PersonEditView(CommonCreateEditView, UpdateView):
    model = Person
    form_class = PersonCreateEditForm
    navbar = 'persons'

    def get_page_title(self):
        return 'Редактирование человека ' + super().get_object().name()


class PersonDeleteView(CommonDeleteView):
    model = Person
    success_url = reverse_lazy('persons')
    navbar = 'persons'

    def get_page_title(self):
        return 'Удаление человека ' + super().get_object().name()


class ImportCreateView(CommonViewMixin, CreateView):
    model = Import
    template_name_suffix = '_create'
    form_class = ImportCreateForm
    navbar = 'persons'
    page_title = 'Импорт из файла'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imports'] = Import.objects.all().order_by('name')
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ImportCreateView, self).dispatch( *args, **kwargs)


def load_csv(import_obj):
    cvs_file = import_obj.file.path
    header = import_obj.header
    numbering = import_obj.numbering

    data = []
    data_header = []
    data_cols = 0

    with open(cvs_file, 'r') as f:
        spamreader = csv.reader(f, delimiter=import_obj.delimiter, quotechar=import_obj.quotechar)
        for row in spamreader:
            if header:
                header -= 1
                data_header.append(row)
                continue
            data_cols = max(data_cols, len(row[numbering:]))
            data.append((row[0:numbering], row[numbering:]))

    return data_header, data, data_cols


class ImportView(CommonViewMixin, UpdateView):
    model = Import
    form_class = ImportUpdateForm
    context_object_name = 'import'
    template_name_suffix = '_edit'
    navbar = 'persons'
    page_title = 'Импорт из файла'

    def get_context_data(self, **kwargs):
        show_all = True if 'show_all' in self.request.GET else False
        context = super().get_context_data(**kwargs)
        obj = super().get_object()
        cvs_file = obj.file.path
        header = obj.header
        numbering = obj.numbering
        show_max = 5

        data_header, data, data_cols = load_csv(obj)

        data_mapping = OrderedDict()
        for field in Person.get_mapped_fields():
            data_mapping[field] = Person._meta.get_field(field).verbose_name
        data_len = len(data)
        show_max = data_len if show_all else show_max
        context['data_mapping'] = data_mapping
        context['numbering'] = range(numbering)
        context['data_cols'] = range(data_cols)
        context['import_header'] = data_header
        context['import_data'] = data[:show_max]
        context['data_len'] = len(data)
        context['data_show_len'] = show_max
        context['added_hospitals'] = Hospital.objects.filter(active_import=obj)
        context['added_persons'] = Person.objects.filter(active_import=obj)

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ImportView, self).dispatch( *args, **kwargs)


class ImportDoView(FormMixin, BaseDetailView):
    model = Import
    form_class = ImportDoForm
    csv_data = None
    data_cols = 0
    http_method_names = ['post']

    def import_data(self, request, *args, **kwargs):
        obj = self.get_object()
        form = self.get_form()
        data_mapping = {}
        persons = []
        if form.is_valid():
            for i in range(self.data_cols):
                field_name = form.cleaned_data['column_%s' % i]
                if field_name:
                    if field_name not in data_mapping:
                        data_mapping[field_name] = i
            for row in self.csv_data:
                person = Person()
                person.cemetery = obj.cemetery
                for field, col in data_mapping.items():
                    val = row[1][col]
                    if len(val) > 255:
                        print(val)
                    person.__setattr__(field, Person.translate_mapped_field_value(field, val, obj))
                    person.active_import = obj
                persons.append(person)

        Person.objects.bulk_create(persons)
        obj.data_added = True
        obj.save()

        return HttpResponseRedirect(obj.get_absolute_url())

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            return self.import_data(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.csv_data is None:
            _, self.csv_data, self.data_cols = load_csv(self.get_object())
        kwargs['columns_count'] = self.data_cols
        return kwargs

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ImportDoView, self).dispatch( *args, **kwargs)


class ImportApplyOrUndoView(View):
    def post(self, request, pk):
        obj = get_object_or_404(Import, id=pk)
        action = request.POST['action']
        if action == 'undo':
            with transaction.atomic():
                Person.objects.filter(active_import=obj).delete()
                Hospital.objects.filter(active_import=obj).delete()
                obj.data_added = False
                obj.save()
            return HttpResponseRedirect(obj.get_absolute_url())
        elif action == 'apply':
            obj.delete()
            return HttpResponseRedirect(reverse_lazy('person_import'))

        return HttpResponseRedirect(obj.get_absolute_url())

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ImportApplyOrUndoView, self).dispatch( *args, **kwargs)
