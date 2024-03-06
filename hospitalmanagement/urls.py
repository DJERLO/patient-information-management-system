from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hospital import views
from django.contrib.auth.views import LoginView,LogoutView




#-------------REST API
from hospital.views import PatientListCreate, PatientRetrieveUpdateDestroy

urlpatterns = [
    path('patients/', PatientListCreate.as_view(), name='patient-list-create'),
    path('patients/id=<int:pk>/', PatientRetrieveUpdateDestroy.as_view(), name='patient-retrieve-update-destroy'),
]
#-------------FOR ADMIN RELATED URLS
urlpatterns = [
    path('admin/', admin.site.urls, name='superadmin'),
    path('api/', include('hospital.urls')),
    path('',views.home_view,name=''),

    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),
    path('contactusSuccess', views.contactussuccess, name='contactussuccess'),  # Adjusted name


    path('adminclick', views.adminclick_view),
    path('doctorclick', views.doctorclick_view),
    path('patientclick', views.patientclick_view),

    path('adminsignup', views.staff_admin_signup_view),
    path('doctorsignup', views.doctor_signup_view,name='doctorsignup'),
    path('patientsignup', views.patient_signup_view),
    
    path('adminlogin', views.adminlogin_view, name='adminlogin'),
    path('adminlogin', LoginView.as_view(template_name='hospital/adminlogin.html')),
    path('adminlogin', LogoutView.as_view(template_name='hospital/adminlogin.html')), # For is_admin logout
    
    path('doctorlogin', views.doctorlogin_view, name='doctorlogin'),
    path('doctorlogin', LoginView.as_view(template_name='hospital/doctorlogin.html')),
    
    path('patientlogin', views.patientlogin_view, name='patientlogin'),
    path('patientlogin', LoginView.as_view(template_name='hospital/patientlogin.html')),

    path('logout', LogoutView.as_view(template_name='hospital/index.html'),name='logout'),
    path('logout/', views.logout_view, name='logout/'),

    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    

    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),

    path('admin-panel', views.admin_panel_view, name='admin-panel'),
    path('admin-view-staff', views.admin_view_staff,name='admin-view-staff'),
    path('admin-approve-staff', views.admin_approve_staff_view,name='admin-approve-staff'),
    
    path('view/staff-details/<int:pk>/', views.admin_staff_details_view, name='admin-staff-details'),
    path('approve-staff/<int:pk>', views.approve_staff_view,name='approve-staff'),
    path('staff-delete/<int:pk>', views.delete_staff_view,name='staff-delete'),




    path('admin-doctor', views.admin_doctor_view,name='admin-doctor'),
    path('admin-view-doctor', views.admin_view_doctor_view,name='admin-view-doctor'),
    path('view/doctor-details/<int:id>/', views.admin_doctor_details_view, name='admin-doctor-details'),

    path('delete-doctor-from-hospital/<int:pk>', views.delete_doctor_from_hospital_view,name='delete-doctor-from-hospital'),
    path('update-doctor/<int:pk>', views.update_doctor_view,name='update-doctor'),
    path('admin-add-doctor', views.admin_add_doctor_view,name='admin-add-doctor'),
    path('admin-approve-doctor', views.admin_approve_doctor_view,name='admin-approve-doctor'),
    path('approve-doctor/<int:pk>', views.approve_doctor_view,name='approve-doctor'),
    path('reject-doctor/<int:pk>', views.reject_doctor_view,name='reject-doctor'),
    path('admin-view-doctor-specialisation',views.admin_view_doctor_specialisation_view,name='admin-view-doctor-specialisation'),


    path('admin-patient', views.admin_patient_view,name='admin-patient'),
    path('admin-view-patient', views.admin_view_patient_view,name='admin-view-patient'),
    path('view/patient-details/<int:patient_id>/', views.admin_patient_details_view, name='admin-patient-details'),
    
    path('delete-patient-from-hospital/<int:pk>', views.delete_patient_from_hospital_view,name='delete-patient-from-hospital'),
    path('update-patient/<int:pk>', views.update_patient_view,name='update-patient'),
    path('admin-add-patient', views.admin_add_patient_view,name='admin-add-patient'),
    path('admin-approve-patient', views.admin_approve_patient_view,name='admin-approve-patient'),
    path('approve-patient/<int:pk>', views.approve_patient_view,name='approve-patient'),
    path('reject-patient/<int:pk>', views.reject_patient_view,name='reject-patient'),
    path('admin-discharge-patient', views.admin_discharge_patient_view,name='admin-discharge-patient'),
    path('discharge-patient/<int:pk>', views.discharge_patient_view,name='discharge-patient'),
    path('download-pdf/<int:pk>', views.download_pdf_view,name='download-pdf'),


    path('admin-appointment', views.admin_appointment_view,name='admin-appointment'),
    path('admin-view-appointment', views.admin_view_appointment_view,name='admin-view-appointment'),
    path('admin-add-appointment', views.admin_add_appointment_view,name='admin-add-appointment'),
    path('admin-approve-appointment', views.admin_approve_appointment_view,name='admin-approve-appointment'),
    path('approve-appointment/<int:pk>', views.approve_appointment_view,name='approve-appointment'),
    path('reject-appointment/<int:pk>', views.reject_appointment_view,name='reject-appointment'),

    path('admin-status-appointment',views.admin_set_status_appointment_view,name='admin-status-appointment'),
    path('completed-appointment-admin/<int:pk>', views.set_admin_complete_appointment_view, name='complete-appointment-admin'),
]   

#---------FOR DOCTOR RELATED URLS-------------------------------------
urlpatterns +=[
    path('get-csrf-token', views.get_csrf_token, name='get_csrf_token'),
    path('doctor-wait-for-approval/', views.doctor_wait_for_approval, name='doctor-wait-for-approval'),
    path('doctor-dashboard', views.doctor_dashboard_view,name='doctor-dashboard'),

    path('doctor-patient', views.doctor_patient_view,name='doctor-patient'),
    path('doctor-view-patient', views.doctor_view_patient_view,name='doctor-view-patient'),
    path('doctor/patient-details/<int:patient_id>/', views.doctor_patient_details_view, name='doctor-patient-details'),
    path('doctor-view-discharge-patient',views.doctor_view_discharge_patient_view,name='doctor-view-discharge-patient'),

    path('doctor-appointment', views.doctor_appointment_view,name='doctor-appointment'),
    path('doctor-view-appointment', views.doctor_view_appointment_view,name='doctor-view-appointment'),
    
    path('doctor-approve-appointment', views.doctor_approve_appointment_view, name='doctor-approve-appointment'),
    path('approve-doctor-appointment/<int:pk>/', views.approve_doctor_appointment_view, name='approve-doctor-appointment'),
    path('reject-doctor-appointment/<int:pk>/', views.reject_doctor_appointment_view, name='reject-doctor-appointment'),
    
    path('doctor-add-appointment', views.doctor_add_appointment_view,name='doctor-add-appointment'),
    path('doctor-status-appointment',views.doctor_set_status_appointment_view,name='doctor-status-appointment'),
    path('set-completed-appointment/<int:pk>', views.set_complete_appointment_view,name='complete-appointment'),
    path('toggle-doctor-status/', views.doctor_toggle_availability, name='toggle-doctor-status'),
]   




#---------FOR PATIENT RELATED URLS-------------------------------------
urlpatterns +=[
    path('patient-dashboard', views.patient_dashboard_view,name='patient-dashboard'),
    path('patient-appointment', views.patient_appointment_view,name='patient-appointment'),
    path('patient-book-appointment', views.patient_book_appointment_view,name='patient-book-appointment'),
    path('patient-view-appointment', views.patient_view_appointment_view,name='patient-view-appointment'),
    path('patient-discharge', views.patient_discharge_view,name='patient-discharge'),
    path('patient-insurance', views.patient_insurance_view,name='patient-insurance'),
]


#---------FOR CHANGING PROFILE URL-------------------------------------
urlpatterns += [
    path('admin-change-profile-pic/', views.admin_change_profile_pic, name='admin-change-profile-pic'),
    path('doctor-change-profile-pic/', views.doctor_change_profile_pic, name='doctor-change-profile-pic'),
    path('patient-change-profile-pic/', views.patient_change_profile_pic, name='patient-change-profile-pic'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

