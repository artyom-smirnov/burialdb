from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView

from website.models import Person, Cemetery, Hospital

from django.utils.translation import ugettext_lazy as _

PAGINATE_BY = 10

class IndexView(TemplateView):
    template_name = "website/index.html"


class BaseListView(ListView):
    paginate_by = PAGINATE_BY
    page_title = 'Untitled'
    navbar = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['navbar'] = self.navbar

        return context


class BurialsView(BaseListView):
    model = Cemetery
    context_object_name = 'cemetery_list'
    page_title = 'Захоронения'
    navbar = 'burials'


class HospitalsView(BaseListView):
    model = Hospital
    context_object_name = 'hospital_list'
    page_title = 'Госпитали'
    navbar = 'hospitals'


class PersonsView(BaseListView):
    model = Person
    context_object_name = 'person_list'
    page_title = 'Люди'
    navbar = 'persons'


class PersonDetailView(DetailView):
    model = Person
    context_object_name = 'person'
