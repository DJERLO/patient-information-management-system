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

#Update Forms
class UpdateDoctorUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username', 'email']
        widgets = {
            'password': forms.PasswordInput()
        }


class UpdateDoctorForm(forms.ModelForm):
    class Meta:
        model = models.Doctor
        fields = ['address', 'mobile', 'department', 'status', 'profile_pic']

#Sign Up
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


class PatientUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

class PatientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        doctors = models.Doctor.objects.filter(status=True)
        choices = [("", "Select Doctor and Department")]  # Add an empty option
        choices += [(doctor.user_id, str(doctor)) for doctor in doctors]
        self.fields['assigned_doctor_id'].choices = choices
        self.fields['assigned_doctor'].choices = [(doctor.user_id, str(doctor)) for doctor in doctors]
    
    # Modify queryset to use user_id instead of id
    assigned_doctor_id = forms.ChoiceField(required=False, widget=forms.Select)
    assigned_doctor = forms.ChoiceField(required=False, widget=forms.Select)
    
    class Meta:
        model = models.Patient
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth', 'address', 'mobile', 'status', 'symptoms', 'profile_pic', 'assigned_doctor', 'assigned_doctor_id']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


class UpdatePatientUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=True)  # Password field adjustment

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

class UpdatePatientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdatePatientForm, self).__init__(*args, **kwargs)
        doctors = models.Doctor.objects.filter(status=True)
        choices = [("", "Select Doctor and Department")]  # Add an empty option
        choices += [(doctor.user_id, str(doctor)) for doctor in doctors]
        self.fields['assigned_doctor_id'].choices = choices
        self.fields['assigned_doctor'].choices = [(doctor.user_id, str(doctor)) for doctor in doctors]
    
    assigned_doctor_id = forms.ChoiceField(required=False, widget=forms.Select)
    assigned_doctor = forms.ChoiceField(required=False, widget=forms.Select)

    

    class Meta:
        model = models.Patient
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth', 'address', 'mobile', 'status', 'symptoms', 'profile_pic', 'assigned_doctor', 'assigned_doctor_id']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


    

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

    def __init__(self, *args, **kwargs):
        patient_doctors = kwargs.pop('patient_doctors', None)
        super(PatientAppointmentForm, self).__init__(*args, **kwargs)

        if patient_doctors:
            self.fields['doctorId'].queryset = patient_doctors

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
