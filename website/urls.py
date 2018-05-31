from django.conf.urls import include, url

from django.urls import path

import website.views as website_views

urlpatterns = [
    path('', website_views.IndexView.as_view()),
    path('burials/', website_views.CemeteriesListView.as_view(), name='cemeteries'),
    path('burials/create/', website_views.CemeteryCreateView.as_view(), name='cemetery_create'),
    path('burials/<int:pk>/', website_views.CemeteryDetailView.as_view(), name='cemetery_detail'),
    path('persons/', website_views.PersonsView.as_view(), name='persons'),
    path('persons/create/', website_views.PersonCreateView.as_view(), name='person_create'),
    path('persons/import/', website_views.ImportCreateView.as_view(), name='person_import'),
    path('persons/import/<int:pk>/edit/', website_views.ImportView.as_view(), name='import_update'),
    path('persons/import/<int:pk>/do/', website_views.ImportDoView.as_view(), name='import_do'),
    path('persons/import/<int:pk>/apply_or_undo/', website_views.ImportApplyOrUndoView.as_view(), name='import_apply_or_undo'),
    path('persons/<int:pk>/edit/', website_views.PersonEditView.as_view(), name='person_edit'),
    path('persons/<int:pk>/delete/', website_views.PersonDeleteView.as_view(), name='person_delete'),
    path('persons/<int:pk>/', website_views.PersonDetailView.as_view(), name='person_detail'),
    path('hospitals/', website_views.HospitalsView.as_view(), name='hospitals'),
    path('hospitals/create/', website_views.HospitalCreateView.as_view(), name='hospital_create'),
    path('hospitals/<int:pk>/', website_views.HospitalDetailView.as_view(), name='hospital_detail'),
]
