from django.core import paginator
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from website.forms import PersonCreateForm
from website.models import Person, Cemetery, Hospital

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
