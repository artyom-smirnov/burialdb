from django.conf.urls import include, url

from django.urls import path

import website.views as website_views

urlpatterns = [
    path('', website_views.IndexView.as_view()),
    path('burials/', website_views.BurialsView.as_view(), name='burials'),
    path('persons/', website_views.PersonsView.as_view(), name='persons'),
    path('persons/<int:pk>/', website_views.PersonDetailView.as_view(), name='person_detail'),
    path('hospitals/', website_views.HospitalsView.as_view(), name='hospitals'),
    path('hospitals/<int:pk>/', website_views.HospitalsView.as_view(), name='hospital_detail'),
]
