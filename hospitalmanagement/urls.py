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
#-------------FOR ADMIN/RECEPTIONIST RELATED URLS
urlpatterns += [
    path('admin/', admin.site.urls, name='superadmin'),
    path('api/', include('hospital.urls')),
    path('',views.home_view,name=''),

    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),
    path('contactusSuccess', views.contactussuccess, name='contactussuccess'),  # Adjusted name


    path('adminclick', views.adminclick_view),
    path('doctorclick', views.doctorclick_view),
    path('receptionistclick', views.receptionistclick_view),
    path('pharmacistclick', views.pharmacistclick_view),
    path('patientclick', views.patientclick_view),

    path('adminsignup', views.staff_admin_signup_view),
    path('pharmacistsignup', views.pharmacist_signup_view,  name='pharmacistsignup'),
    path('doctorsignup', views.doctor_signup_view, name='doctorsignup'),
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

    path('admin-admission',views.admin_admission_view,name='admin-admission'),
    path('admin-activate-patient/<int:pk>',views.reactivate_patient_view,name='admin-activate-patient'),

    path('admin-billing-invoice', views.admin_billing_view, name='admin-billing-invoice'),
    path('admin-view-unpaid-bills', views.admin_unpaid_bills_view, name='admin-view-unpaid-bills'),
    path('admin-view-patient-invoice/<int:patientId>/<int:discharge_id>', views.admin_view_patient_invoice, name='admin-view-patient-invoice'),
    path('mark-as-paid/<int:patientId>/<int:discharge_id>',views.mark_pay_patient_bill,name='mark-as-paid'),

    path('admin-view-paid-bills', views.admin_patient_discharge_records_view, name='admin-view-paid-bills'),
    path('admin-view-invoice-records/<int:patientId>', views.admin_patient_view_records, name='admin-view-invoice-records'),

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
    path('download-pdf/<int:pk>/<int:discharge_id>/', views.download_pdf_view, name='download-pdf'),

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

#---------FOR PHARMACIST RELATED URLS-------------------------------------
urlpatterns +=[
    path('pharmacist-dashboard', views.pharmacist_dashboard_view, name='pharmacist-dashboard'),
    path('pharmacist-medicines', views.pharmacist_medicines_view, name='pharmacist-medicines'),
    path('pharmacist-view-medicines', views.pharmacist_medicines_list_view, name='pharmacist-view-medicines'),
    path('pharmacist-view-medicine/<int:pk>', views.pharmacist_view_medicine, name='pharmacist-view-medicine'),
    path('pharmacist-add-medicine', views.pharmacist_add_medicine, name='pharmacist-add-medicine'),
    path('pharmacist-update-medicine/<int:pk>', views.pharmacist_update_medicine, name='pharmacist-update-medicine'),
    path('pharmacist-manufacturers-view', views.pharmacist_manufacturers_view, name='pharmacist-manufacturers-view'),
    path('pharmacist-manufacturers-update', views.pharmacist_manufacturers_update, name='pharmacist-manufacturers-update'),
    path('pharmacist-manufacturers-delete', views.pharmacist_manufacturers_delete, name='pharmacist-manufacturers-delete'),
]


#---------FOR PATIENT RELATED URLS-------------------------------------
urlpatterns +=[ 
    path('create-payment-session/', views.create_payment_session, name='create_payment_session'),
    path('payment-expire/', views.set_checkout_expiry_date, name='get_checkout_expiry_date'),
    path('view-success-payment/', views.success_payment_view, name='view-success-payment'),
    path('view-failed-payment/', views.failed_payment_view, name='view-failed-payment'),
    path('patient-dashboard', views.patient_dashboard_view,name='patient-dashboard'),
    path('patient-appointment', views.patient_appointment_view,name='patient-appointment'),
    path('patient-book-appointment', views.patient_book_appointment_view,name='patient-book-appointment'),
    path('patient-view-appointment', views.patient_view_appointment_view,name='patient-view-appointment'),
    path('patient-discharge', views.patient_discharge_view,name='patient-discharge'),
    path('patient-insurance', views.patient_insurance_view,name='patient-insurance'),
]


#---------FOR USER SETTINGS URL-------------------------------------
urlpatterns += [
    path('admin-update-profile-details/', views.admin_update_profile_details, name='admin-update-profile-details'),
    path('pharmacist-update-profile/', views.pharmacist_update_profile_details, name='pharmacist-update-profile'),
    path('doctor-update-profile/', views.doctor_update_profile, name='doctor-update-profile'),
    path('patient-update-profile-details/', views.patient_update_profile_details, name='patient-update-profile-details'),
]

#------AUTOCOMPLETION QUERY URLS------------------------------------
urlpatterns+=[
    path('autocomplete/', views.autocomplete_view, name='autocomplete'),
]

#---- Agents 
urlpatterns +=[
    # Other URL patterns...
     path('webhooks', views.handle_webhook, name='webhooks'),
     path('chatgpt4/', views.chatgpt4, name='chatgpt4'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

