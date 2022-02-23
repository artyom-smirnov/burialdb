from django.conf.urls import include, url

from django.urls import path

import website.views as website_views

urlpatterns = [
    path('', website_views.IndexView.as_view()),
    path('burials/', website_views.CemeteriesListView.as_view(), name='cemeteries'),
    path('burials/create/', website_views.CemeteryCreateView.as_view(), name='cemetery_create'),
    path('burials/<int:pk>/', website_views.CemeteryDetailView.as_view(), name='cemetery_detail'),
    path('burials/<int:pk>/edit/', website_views.CemeteryEditView.as_view(), name='cemetery_edit'),
    path('burials/<int:pk>/delete/', website_views.CemeteryDeleteView.as_view(), name='cemetery_delete'),
    path('burials/<int:pk>/export/', website_views.CemeteryExportView.as_view(), name='cemetery_export'),
    path('persons/', website_views.PersonsView.as_view(), name='persons'),
    path('persons/create/', website_views.PersonCreateView.as_view(), name='person_create'),
    path('persons/import/', website_views.ImportsListView.as_view(), name='import_list'),
    path('persons/import/create/', website_views.ImportCreateView.as_view(), name='person_import'),
    path('persons/import/<int:pk>/', website_views.ImportView.as_view(), name='import_view'),
    path('persons/import/<int:pk>/edit/', website_views.ImportEditView.as_view(), name='import_edit'),
    path('persons/import/<int:pk>/delete/', website_views.ImportDeleteView.as_view(), name='import_delete'),
    path('persons/import/<int:pk>/do_cancel/', website_views.ImportDoView.as_view(), name='import_do_cancel'),
    path('persons/import/<int:pk>/apply_or_undo/', website_views.ImportApplyOrUndoView.as_view(), name='import_apply_or_undo'),
    path('persons/<int:pk>/edit/', website_views.PersonEditView.as_view(), name='person_edit'),
    path('persons/<int:pk>/delete/', website_views.PersonDeleteView.as_view(), name='person_delete'),
    path('persons/<int:pk>/', website_views.PersonDetailView.as_view(), name='person_detail'),
    path('hospitals/', website_views.HospitalsView.as_view(), name='hospitals'),
    path('hospitals/create/', website_views.HospitalCreateView.as_view(), name='hospital_create'),
    path('hospitals/<int:pk>/', website_views.HospitalDetailView.as_view(), name='hospital_detail'),
    path('hospitals/<int:pk>/edit/', website_views.HospitalEditView.as_view(), name='hospital_edit'),
    path('hospitals/<int:pk>/delete/', website_views.HospitalDeleteView.as_view(), name='hospital_delete'),
]
