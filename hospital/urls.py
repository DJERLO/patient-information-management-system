from django.urls import path
from .views import PatientListCreate, PatientRetrieveUpdateDestroy



urlpatterns = [
    path('patients/', PatientListCreate.as_view(), name='patient-list-create'),
    path('patients/id=<int:pk>/', PatientRetrieveUpdateDestroy.as_view(), name='patient-retrieve-update-destroy'),
]