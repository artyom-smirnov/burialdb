import csv
from collections import OrderedDict

from django.core import paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import ProcessFormView, ModelFormMixin, BaseUpdateView, FormMixin

from website.forms import PersonCreateForm, ImportCreateForm, ImportUpdateForm, ImportDoForm
from website.models import Person, Cemetery, Hospital, Import

from django.utils.translation import ugettext_lazy as _

PAGINATE_BY = 10


class CommonViewMixin(object):
    paginate_by = PAGINATE_BY
    page_title = 'Untitled'
    navbar = None

    def get_page_title(self):
        return self.page_title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_page_title()
        context['navbar'] = self.navbar

        return context


class BaseListView(CommonViewMixin, ListView):
    pass


class DetailWithListView(CommonViewMixin, DetailView):
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


class IndexView(TemplateView):
    template_name = "website/index.html"


class CemeteriesListView(BaseListView):
    model = Cemetery
    context_object_name = 'cemetery_list'
    page_title = 'Захоронения'
    navbar = 'burials'


class CemeteryDetailView(DetailWithListView):
    model = Cemetery
    list_model = Person
    context_object_name = 'cemetery'
    navbar = 'burials'

    def get_page_title(self):
        return 'Захоронение ' + super().get_object().name

    def get_list_queryset(self):
        obj = super().get_object()
        return Person.objects.filter(Q(cemetery=obj) | Q(cemetery_actual=obj))


class HospitalsView(BaseListView):
    model = Hospital
    context_object_name = 'hospital_list'
    page_title = 'Госпитали'
    navbar = 'hospitals'


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


class PersonsView(BaseListView):
    model = Person
    context_object_name = 'person_list'
    navbar = 'persons'
    page_title = 'Люди'


class PersonDetailView(CommonViewMixin, DetailView):
    model = Person
    context_object_name = 'person'
    navbar = 'persons'

    def get_page_title(self):
        return super().get_object().name()


class PersonCreateView(CommonViewMixin, CreateView):
    model = Person
    template_name_suffix = '_create'
    form_class = PersonCreateForm
    navbar = 'persons'
    page_title = 'Добавление нового человека'


class PersonEditView(CommonViewMixin, UpdateView):
    model = Person
    form_class = PersonCreateForm
    template_name_suffix = '_edit'
    navbar = 'persons'

    def get_page_title(self):
        return 'Редактирование ' + super().get_object().name()


class PersonDeleteView(CommonViewMixin, DeleteView):
    model = Person
    success_url = reverse_lazy('persons')
    navbar = 'persons'

    def get_page_title(self):
        return 'Удаление ' + super().get_object().name()


class ImportCreateView(CommonViewMixin, CreateView):
    model = Import
    template_name_suffix = '_create'
    form_class = ImportCreateForm
    navbar = 'persons'
    page_title = 'Импорт из файла'


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
    navbar = 'import'
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

        print(data)
        return context


class ImportDoView(FormMixin, BaseDetailView):
    model = Import
    form_class = ImportDoForm
    csv_data = None
    data_cols = 0
    http_method_names = ['post']

    def import_data(self, request, *args, **kwargs):
        obj = self.get_object()
        print(obj)
        form = self.get_form()
        data_mapping = {}
        if form.is_valid():
            for i in range(self.data_cols):
                field_name = form.cleaned_data['column_%s' % i]
                if (field_name):
                    if field_name not in data_mapping:
                        data_mapping[field_name] = i
            for row in self.csv_data:
                for field, col in data_mapping.items():
                    val = row[1][col]
                    person = Person()
                    person.__setattr__(field, val)
                    person.save()
                    break
                    # print('field %s = %s' % (field, row[1][col]))

        # """
        # Call the delete() method on the fetched object and then redirect to the
        # success URL.
        # """
        # self.object = self.get_object()
        # success_url = self.get_success_url()
        # self.object.delete()
        # return HttpResponseRedirect('/')
        return

    def post(self, request, *args, **kwargs):
        return self.import_data(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.csv_data is None:
            _, self.csv_data, self.data_cols = load_csv(self.get_object())
        kwargs['columns_count'] = self.data_cols
        return kwargs
