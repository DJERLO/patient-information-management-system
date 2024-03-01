from django.contrib import admin
from .models import HospitalStaffAdmin, Doctor,Patient, Appointment,PatientDischargeDetails, Insurance

# Register your models here.
class HospitalStaffAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'profile_pic', 'address', 'mobile', 'email')
    # Add any other configuration options you need

admin.site.register(HospitalStaffAdmin, HospitalStaffAdminAdmin)

class DoctorAdmin(admin.ModelAdmin):
    pass
admin.site.register(Doctor, DoctorAdmin)

class PatientAdmin(admin.ModelAdmin):
    pass
admin.site.register(Patient, PatientAdmin)

class AppointmentAdmin(admin.ModelAdmin):
    pass
admin.site.register(Appointment, AppointmentAdmin)

class InsuranceAdmin(admin.ModelAdmin):
    pass
admin.site.register(Insurance, InsuranceAdmin)

class PatientDischargeDetailsAdmin(admin.ModelAdmin):
    pass
admin.site.register(PatientDischargeDetails, PatientDischargeDetailsAdmin)
