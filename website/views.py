from collections import OrderedDict
import json
import base64
import hashlib
import urllib

from django.contrib.auth.decorators import login_required
from django.core import paginator
from django.db import transaction
from django.db.models import Q, Count, F
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import ContextMixin
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import FormMixin, FormView
from django.views.generic.list import MultipleObjectMixin

from website.forms import PersonCreateEditForm, ImportCreateForm, ImportEditForm, ImportDoForm, HospitalCreateEditForm, \
    CemeteryCreateEditForm, PersonSearchForm
from website.importer import ImporterFactory
from website.models import Person, Cemetery, Hospital, Import, SearchData

PAGINATE_BY = 50


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


class CommonPaginatedViewMixin(MultipleObjectMixin, CommonViewMixin):
    paginate_by = PAGINATE_BY

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        if not context.get('is_paginated', False):
            return context

        paginator = context.get('paginator')
        num_pages = paginator.num_pages
        current_page = context.get('page_obj')
        page_no = current_page.number

        if num_pages <= 11 or page_no <= 6:  # case 1 and 2
            pages = [x for x in range(1, min(num_pages + 1, 12))]
        elif page_no > num_pages - 6:  # case 4
            pages = [x for x in range(num_pages - 10, num_pages + 1)]
        else:  # case 3
            pages = [x for x in range(page_no - 5, page_no + 6)]

        context.update(
            {
                'pages': pages,
                'page_no': page_no,
                'num_pages': num_pages
            }
        )

        return context


class BaseListView(CommonPaginatedViewMixin, ListView):
    pass


class DetailWithListView(CommonPaginatedViewMixin, DetailView):
    list_model = None

    def get_list_queryset(self):
        return self.list_model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.get_list_queryset()
        objects_paginator, page, objects_list, has_other_pages = self.paginate_queryset(queryset, PAGINATE_BY)

        newcontext = {}
        newcontext['object'] = self.object
        context_object_name = self.get_context_object_name(self.object)
        if context_object_name:
            newcontext[context_object_name] = self.object
        newcontext['page_obj'] = page
        newcontext['paginator'] = objects_paginator
        newcontext['is_paginated'] = True if objects_paginator.num_pages > 1 else False
        newcontext['list_obj'] = objects_list

        context.update(newcontext)
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
    page_title = 'Мемориалы'
    navbar = 'burials'

    def get_queryset(self):
        q = super().get_queryset()
        q = q.annotate(
            person_count=Count('person_cemetery'),
            person_actual_count=Count('person_cemetery_actual'),
            person_total_count=F('person_count') + F('person_actual_count')
        )
        return q

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            self.object_list = self.get_queryset()
            allow_empty = self.get_allow_empty()
            context = self.get_context_data()
            content = loader.render_to_string('website/snippets/cemetery_list_rows.html', context, request)
            return JsonResponse({"content": content})
        else:
            return super().get(request, args, kwargs)


class CemeteryDetailView(DetailWithListView):
    model = Cemetery
    list_model = Person
    context_object_name = 'cemetery'
    navbar = 'burials'

    def get_page_title(self):
        return 'Мемориал ' + super().get_object().name

    def get_list_queryset(self):
        obj = super().get_object()
        return Person.objects.filter(Q(active_import=None) & (Q(cemetery=obj) | Q(cemetery_actual=obj))).order_by('screen_name')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = self.get_list_queryset().count
        context['start_item_number'] = ((context['page_obj'].number - 1) * PAGINATE_BY) + 1
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object_list = self.get_list_queryset()
        if request.is_ajax():
            context = self.get_context_data(object=self.object)
            context['person_list'] = context['list_obj']
            content = loader.render_to_string('website/snippets/person_list_rows.html', context, request)
            return JsonResponse({"content": content})
        else:
            return super().get(request, args, kwargs)



class CemeteryCreateView(CommonCreateEditView):
    model = Cemetery
    form_class = CemeteryCreateEditForm
    navbar = 'burials'
    page_title = 'Добавление нового мемориала'


class CemeteryEditView(CommonCreateEditView, UpdateView):
    model = Cemetery
    form_class = CemeteryCreateEditForm
    navbar = 'burials'
    page_title = 'Редактирование мемориала'

    def get_page_title(self):
        return 'Редактирование мемориала ' + super().get_object().name


class CemeteryExportView(DetailView):
    model = Cemetery

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        persons = Person.objects.filter(cemetery=self.object)

        def cond(f):
           return f.attname in ('id', 'active_import_id', 'cemetery_id', 'cemetery_actual_id') \
                  or f.attname.endswith('_actual')
        fields = [f.attname for f in Person._meta.fields if not cond(f)]
        captions = [f.verbose_name for f in Person._meta.fields if not cond(f)]

        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active

        ws.append(captions)

        for person in persons:
            row = []
            for f in fields:
                val = getattr(person, f)
                if f == 'state':
                    val = person.screen_state()
                row.append(val)
            ws.append(row)

        wb.save('/tmp/export.xlsx')
        encoded_filename = urllib.parse.quote(self.object.name, encoding='utf-8')

        with open('/tmp/export.xlsx', 'rb') as f:
            response = HttpResponse(
                        f.read(),
                        content_type=wb.mime_type
                    )
            response['Content-Disposition'] = 'attachment; filename*=UTF8\'\'%s.xlsx' % encoded_filename
        return response


class CemeteryDeleteView(CommonDeleteView):
    model = Cemetery
    success_url = reverse_lazy('cemeteries')
    navbar = 'burials'
    additional_text = 'При удалении мемориала, люди добавленные в него не удалятся!'

    def get_page_title(self):
        return 'Удаление мемориала ' + super().get_object().name


class HospitalsView(BaseListView):
    model = Hospital
    context_object_name = 'hospital_list'
    page_title = 'Госпитали'
    navbar = 'hospitals'

    def get_queryset(self):
        q = super().get_queryset()
        q = q.annotate(
            person_total_count=Count('person_hospital_actual')
        )
        return q

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            self.object_list = self.get_queryset()
            allow_empty = self.get_allow_empty()
            context = self.get_context_data()
            content = loader.render_to_string('website/snippets/hospitals_list_rows.html', context, request)
            return JsonResponse({"content": content})
        else:
            return super().get(request, args, kwargs)


class HospitalDetailView(DetailWithListView):
    model = Hospital
    list_model = Person
    context_object_name = 'hospital'
    navbar = 'hospitals'

    def get_page_title(self):
        return 'Госпиталь ' + super().get_object().name

    def get_list_queryset(self):
        obj = super().get_object()
        return Person.objects.filter(Q(hospital=obj) | Q(hospital_actual=obj)).order_by('screen_name')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = self.get_list_queryset().count
        context['start_item_number'] = ((context['page_obj'].number - 1) * PAGINATE_BY) + 1
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object_list = self.get_list_queryset()
        if request.is_ajax():
            context = self.get_context_data(object=self.object)
            context['person_list'] = context['list_obj']
            content = loader.render_to_string('website/snippets/person_list_rows.html', context, request)
            return JsonResponse({"content": content})
        else:
            return super().get(request, args, kwargs)


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


class PersonsView(FormMixin, BaseListView):
    model = Person
    context_object_name = 'person_list'
    navbar = 'persons'
    page_title = 'Люди'
    form_class = PersonSearchForm
    http_method_names = ['get', 'post']
    search = None

    def get_search(self):
        if 'q' in self.request.GET:
            if not self.search:
                self.search = get_object_or_404(SearchData, id=self.request.GET['q'])
        return self.search

    def get_queryset(self):
        form = self.form_class(self.request.GET)
        q = Person.objects.filter(active_import=None).order_by('screen_name')
        if 'q' in self.request.GET:
            search = self.get_search()
            fields = json.loads(search.fields)

            for k, v in Person.get_search_mapping().items():
                if k in fields:
                    val = fields[k]
                    filter = Q()
                    for field in v:
                        if field == 'state' and val == '-1':
                            args = {'state__isnull': True}
                        else:
                            args = {'%s%s' % (field, Person._search_filters_mapping[k]): val}
                        filter |= Q(**args)
                    q = q.filter(filter)
        return q

    def get_context_data(self, *, object_list=None, **kwargs):
        search = self.get_search()
        if search:
            self.initial = json.loads(search.fields)
        context = super().get_context_data(**kwargs)
        context['have_imports'] = Import.objects.count() > 0
        context['show_cemetery'] = True
        context['total_count'] = self.get_queryset().count
        context['start_item_number'] = ((context['page_obj'].number - 1) * PAGINATE_BY) + 1
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return HttpResponseRedirect(reverse('persons'))

        fields = {
            'advanced_search': form.cleaned_data['advanced_search'],
        }
        for k, _ in Person.get_search_mapping().items():
            if form.cleaned_data[k]:
                val = form.cleaned_data[k]
                fields[k] = val

        fields = json.dumps(fields)
        hash = hashlib.sha1()
        hash.update(fields.encode('utf-8'))
        hash = hash.digest()
        try:
            search = SearchData.objects.get(hash=hash)
        except SearchData.DoesNotExist as e:
            search = None
        if not search:
            search = SearchData.objects.create(hash=hash, fields=fields)
        return HttpResponseRedirect('%s?q=%s' % (reverse_lazy('persons'), search.id))



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
                    if field == 'state':
                        try:
                            val = int(val)
                            if val not in [i[0] for i in Person.STATES]:
                                val = None
                        except:
                            val = None
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
