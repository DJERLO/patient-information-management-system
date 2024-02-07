from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . import models

#Login Forms
class AdminLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())

class DoctorLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())

class PatientLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())

#for admin signup
class StaffAdminSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class StaffAdminProfileForm(forms.ModelForm):
    class Meta:
        model = models.HospitalStaffAdmin
        fields = ['profile_pic', 'address', 'mobile']


class UpdateDoctorUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username', 'email']
        widgets = {
            'password': forms.PasswordInput()
        }


#Update Forms
class UpdateDoctorForm(forms.ModelForm):
    class Meta:
        model = models.Doctor
        fields = ['address', 'mobile', 'department', 'status', 'profile_pic']

class DoctorUserForm(UserCreationForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username', 'email', 'password1', 'password2']
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }
        
class DoctorForm(forms.ModelForm):
    class Meta:
        model = models.Doctor
        fields = ['address', 'mobile', 'department', 'status', 'profile_pic']
    
    def __init__(self, *args, **kwargs):
        super(DoctorForm, self).__init__(*args, **kwargs)
        self.fields['department'].required = True
        self.fields['status'].required = False
        self.fields['address'].required = True
        self.fields['mobile'].required = True


#for teacher related form
class PatientUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
        
class PatientForm(forms.ModelForm):
    #this is the extrafield for linking patient and their assigend doctor
    #this will show dropdown __str__ method doctor model is shown on html so override it
    #to_field_name this will fetch corresponding value  user_id present in Doctor model and return it
    assignedDoctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Name and Department", to_field_name="user_id")
    class Meta:
        model=models.Patient
        fields=['address','mobile','status','symptoms','profile_pic']


class AppointmentForm(forms.ModelForm):
    doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Doctor Name and Department", to_field_name="user_id")
    patientId=forms.ModelChoiceField(queryset=models.Patient.objects.all().filter(status=True),empty_label="Patient Name and Symptoms", to_field_name="user_id")
    
    class Meta:
        model=models.Appointment
        fields=['description','status', 'appointmentDate']
        widgets = {
            'appointmentDate': forms.DateInput(attrs={'type': 'datetime-local'}),
        }

class DoctorAppointmentForm(forms.ModelForm):
    patientId=forms.ModelChoiceField(queryset=models.Patient.objects.all().filter(status=True),empty_label="Patient Name and Symptoms", to_field_name="user_id")
    
    def __init__(self, *args, **kwargs):
        doctor_patients = kwargs.pop('doctor_patients', None)
        super(DoctorAppointmentForm, self).__init__(*args, **kwargs)

        if doctor_patients:
            self.fields['patientId'].queryset = doctor_patients


    class Meta:
        model = models.Appointment
        fields = ['description', 'status', 'appointmentDate']
        widgets = {
            'appointmentDate': forms.DateInput(attrs={'type': 'datetime-local'}),
        }

class PatientAppointmentForm(forms.ModelForm):
    doctorId = forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True), empty_label="Doctor Name and Department", to_field_name="user_id")

    class Meta:
        model = models.Appointment
        fields = ['description', 'status', 'appointmentDate']
        widgets = {
            'appointmentDate': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }





#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Subject = forms.CharField(max_length=30)
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))



#Developed By : sumit kumar
#facebook : fb.com/sumit.luv
#Youtube :youtube.com/lazycoders
