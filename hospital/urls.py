from django.urls import path
from .views import PatientListCreate, PatientRetrieveUpdateDestroy, DoctorDepartmentListView, PharmacistSpecializationListView



urlpatterns = [
    path('pharmacist/specializations', PharmacistSpecializationListView.as_view(), name='pharmacist-specializations'),
    path('departments/', DoctorDepartmentListView.as_view(), name='doctor-departments'),
    path('patients/', PatientListCreate.as_view(), name='patient-list-create'),
    path('patients/id=<int:pk>/', PatientRetrieveUpdateDestroy.as_view(), name='patient-retrieve-update-destroy'),
]