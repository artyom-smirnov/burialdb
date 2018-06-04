from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.core import paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import ContextMixin
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import FormMixin
from django.db import transaction

from website.importer import ImporterFactory
from website.forms import PersonCreateEditForm, ImportCreateForm, ImportEditForm, ImportDoForm, HospitalCreateEditForm, \
    CemeteryCreateEditForm
from website.models import Person, Cemetery, Hospital, Import

PAGINATE_BY = 10


class CommonViewMixin(ContextMixin):
    page_title = 'Untitled'
    navbar = None

    def get_page_title(self):
        return self.page_title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_page_title()
        context['navbar'] = self.navbar

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CommonViewMixin, self).dispatch(*args, **kwargs)


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


class CommonDeleteView(CommonViewMixin, DeleteView):
    model = None
    success_url = None
    navbar = None
    template_name = 'website/common_confirm_delete.html'
    additional_text = None

    def get_page_title(self):
        return 'Удаление ' + super().get_object().name()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['additional_text'] = self.additional_text
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
        return Person.objects.filter(Q(active_import=None) & (Q(cemetery=obj) | Q(cemetery_actual=obj)))


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
    additional_text = 'При удалении захоронения, люди добавленные в него не удалятся!'

    def get_page_title(self):
        return 'Удаление захоронения ' + super().get_object().name


class HospitalsView(BaseListView):
    model = Hospital
    context_object_name = 'hospital_list'
    page_title = 'Госпитали'
    navbar = 'hospitals'

    def get_queryset(self):
        return Hospital.objects.filter(active_import=None)


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
    additional_text = 'При удалении госпиталя, люди добавленные в него не удалятся!'

    def get_page_title(self):
        return 'Удаление госпиталя ' + super().get_object().name


class PersonsView(BaseListView):
    model = Person
    context_object_name = 'person_list'
    navbar = 'persons'
    page_title = 'Люди'

    def get_queryset(self):
        return Person.objects.filter(active_import=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['have_imports'] = Import.objects.count() > 0
        return context


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


class ImportsListView(BaseListView):
    model = Import
    context_object_name = 'import_list'
    page_title = 'Незавершенные импорты'
    navbar = 'persons'


class ImportCreateView(CommonCreateEditView):
    model = Import
    form_class = ImportCreateForm
    navbar = 'persons'
    page_title = 'Импорт из файла'


class ImportEditView(CommonCreateEditView, UpdateView):
    model = Import
    form_class = ImportEditForm
    navbar = 'persons'

    def get_page_title(self):
        return 'Редактирование импорта ' + super().get_object().name


class ImportDeleteView(CommonDeleteView):
    model = Import
    success_url = reverse_lazy('import_list')
    navbar = 'persons'

    def get_page_title(self):
        return 'Удаление импорта ' + super().get_object().name


class ImportView(CommonViewMixin, UpdateView):
    model = Import
    form_class = ImportEditForm
    context_object_name = 'import'
    template_name_suffix = '_detail'
    navbar = 'persons'
    page_title = 'Импорт из файла'

    def get_context_data(self, **kwargs):
        show_all = True if 'show_all' in self.request.GET else False
        context = super().get_context_data(**kwargs)
        obj = super().get_object()
        numbering = obj.numbering
        show_max = 5
        data_header = 0
        data_cols = 0
        data = []
        error = None

        try:
            importer = ImporterFactory(obj).get_importer()
            data_header, data, data_cols = importer.import_data()
        except Exception as e:
            error = str(e)

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
        context['error'] = error

        return context


class ImportDoView(FormMixin, BaseDetailView):
    model = Import
    form_class = ImportDoForm
    csv_data = None
    data_cols = 0
    http_method_names = ['post']

    def import_data(self):
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
                    person.__setattr__(field, Person.translate_mapped_field_value(field, val, obj))
                    person.active_import = obj
                persons.append(person)

        Person.objects.bulk_create(persons)
        obj.data_added = True
        obj.save()

        return HttpResponseRedirect(obj.get_absolute_url())

    def post(self, request, pk):
        with transaction.atomic():
            return self.import_data()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.csv_data is None:
            importer = ImporterFactory(self.get_object()).get_importer()
            _, self.csv_data, self.data_cols = importer.import_data()
        kwargs['columns_count'] = self.data_cols
        return kwargs

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ImportDoView, self).dispatch(*args, **kwargs)


class ImportApplyOrUndoView(View):
    http_method_names = ['post']

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
        return super(ImportApplyOrUndoView, self).dispatch(*args, **kwargs)
