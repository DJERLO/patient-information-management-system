from datetime import timezone
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . import models

#Modal Forms
class AdminChangeProfilePicForm(forms.ModelForm):
    class Meta:
        model = models.HospitalStaffAdmin
        fields = ['profile_pic']

class DoctorChangeProfilePicForm(forms.ModelForm):
    class Meta:
        model = models.Doctor
        fields = ['profile_pic']

class PatientChangeProfilePicForm(forms.ModelForm):
    class Meta:
        model = models.Patient
        fields = ['profile_pic']

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

# for admin signup
class StaffAdminSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=True,
    )
    password2 = forms.CharField(
        label=("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        required=True,
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class StaffAdminProfileForm(forms.ModelForm):
    profile_pic = forms.ImageField(required=True)
    address = forms.CharField(max_length=100, required=True)
    mobile = forms.CharField(max_length=12, required=True)

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
        fields = ['address', 'mobile', 'department', 'profile_pic', 'license_num']
        widgets = {
            'profile_pic': forms.FileInput(attrs={'required': 'required'}),
        }

# Sign Up
class DoctorUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super(DoctorUserForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True

class DoctorForm(forms.ModelForm):
    class Meta:
        model = models.Doctor
        fields = ['address', 'mobile', 'department', 'profile_pic', 'license_num']
        widgets = {
            'mobile': forms.TextInput(attrs={'pattern': r'(^(\+)(\d){12}$)|(^\d{11}$)', 'required': 'required'}),
            'license_num': forms.TextInput(attrs={'pattern': r'^\d{7}$', 'required': 'required'}),
            'profile_pic': forms.FileInput(attrs={'required': 'required'}),
        }
    
    


class PatientUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'required': 'required'}),
            'last_name': forms.TextInput(attrs={'required': 'required'}),
            'email': forms.EmailInput(attrs={'required': 'required'}),
            'username': forms.TextInput(attrs={'required': 'required'}),
            'password': forms.PasswordInput(attrs={'required': 'required'}),
        }

class PatientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        doctors = models.Doctor.objects.filter(status=True)
        choices = [("", "Select Doctor and Department")]  # Add an empty option
        choices += [(doctor.user_id, str(doctor)) for doctor in doctors]
        self.fields['assigned_doctor_id'].choices = choices
        self.fields['assigned_doctor'].choices = [(doctor.user_id, str(doctor)) for doctor in doctors]
    
    # Modify queryset to use user_id instead of id
    assigned_doctor_id = forms.ChoiceField(required=True, widget=forms.Select(attrs={'required': 'required'}))
    assigned_doctor = forms.ChoiceField(required=False)
    
    
    class Meta:
        model = models.Patient
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth', 'address', 'mobile', 'status', 'symptoms', 'profile_pic', 'assigned_doctor', 'assigned_doctor_id']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'required': 'required'}),
            'address': forms.TextInput(attrs={'required': 'required'}),
            'mobile': forms.TextInput(attrs={'pattern': r'(^(\+)(\d){12}$)|(^\d{11}$)', 'required': 'required'}),
            'symptoms': forms.TextInput(attrs={'required': 'required'}),
            'profile_pic': forms.FileInput(attrs={'required': 'required'}),
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
    doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=models.Doctor.STATUS_AVAILABLE),empty_label="Doctor Name and Department", to_field_name="user_id")
    patientId=forms.ModelChoiceField(queryset=models.Patient.objects.all().filter(status=True),empty_label="Patient Name and Symptoms", to_field_name="user_id")
    
    class Meta:
        model=models.Appointment
        fields=['description','status', 'appointmentDate']
        widgets = {
            'appointmentDate': forms.DateInput(attrs={'type': 'datetime-local'}),
        }

class DoctorAppointmentForm(forms.ModelForm):
    patientId=forms.ModelChoiceField(queryset=models.Patient.objects.all().filter(status=models.Doctor.STATUS_AVAILABLE),empty_label="Patient Name and Symptoms", to_field_name="user_id")
    
    def __init__(self, *args, **kwargs):
        doctor_patients = kwargs.pop('doctor_patients', None)
        super(DoctorAppointmentForm, self).__init__(*args, **kwargs)

        if doctor_patients:
            self.fields['patientId'].queryset = doctor_patients


    class Meta:
        model = models.Appointment
        fields = ['description', 'appointmentDate']
        widgets = {
            'appointmentDate': forms.DateInput(attrs={'type': 'datetime-local'}),
        }

class PatientAppointmentForm(forms.ModelForm):
    doctorId = forms.ModelChoiceField(queryset=models.Doctor.objects.none(), empty_label="Your Doctor Is Not Available", to_field_name="user_id")
    
    def __init__(self, *args, **kwargs):
        patient_doctors = kwargs.pop('patient_doctors', None)
        super(PatientAppointmentForm, self).__init__(*args, **kwargs)
        
        if patient_doctors:
            self.fields['doctorId'].queryset = patient_doctors.filter(status=models.Doctor.STATUS_AVAILABLE)
            self.fields['doctorId'].empty_label = "Doctor Name and Department"
            if not self.fields['doctorId'].queryset.exists():
                self.fields['doctorId'].empty_label = "No available doctors"
                self.fields['doctorId'].widget.attrs['disabled'] = 'disabled'

    class Meta:
        model = models.Appointment
        fields = ['description', 'status', 'appointmentDate']
        widgets = {
            'appointmentDate': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class InsuranceForm(forms.ModelForm):
    class Meta:
        model = models.Insurance
        fields = ['insurance_provider', 'policy_number', 'group_number', 'effective_date', 'expiration_date', 'copayment_info']
        widgets = {
            'effective_date': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }

#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30, required=True)
    Email = forms.EmailField(required=True)
    Subject = forms.CharField(max_length=30, required=True)
    Message = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}), required=True)


