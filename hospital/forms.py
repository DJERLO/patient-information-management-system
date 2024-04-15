from datetime import timezone
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .departments import SPECIALIZATION_CHOICES
from . import models
from django.core.validators import RegexValidator


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
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
        validators=[
            RegexValidator(
                regex='^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()\-_=+{};:,<.>])(?=.*\w).{8,}$',
                message="Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one digit, and one special character.",
            ),
        ],
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

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
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
        validators=[
            RegexValidator(
                regex='^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()\-_=+{};:,<.>])(?=.*\w).{8,}$',
                message="Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one digit, and one special character.",
            ),
        ],
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'required': 'required'}),
            'last_name': forms.TextInput(attrs={'required': 'required'}),
            'email': forms.EmailInput(attrs={'required': 'required'}),
            'username': forms.TextInput(attrs={'required': 'required'}),
            'password1': forms.PasswordInput(attrs={'required': 'required'}),
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
    password = forms.CharField(widget=forms.PasswordInput(), required=False)  # Password field adjustment

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

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
        fields=['description', 'appointmentDate']
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
        fields = ['description', 'appointmentDate']
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

# For Pharmacist User Creation
class PharmacistUserSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

class PharmacistSignUpForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    contact_email = forms.EmailField(required=True)
    contact_phone = forms.CharField(max_length=20, required=True)
    license_number = forms.CharField(max_length=7, required=True, widget=forms.TextInput(attrs={'pattern': '[0-9]{7}', 'title': 'License number must be 7 digits.'}))
    address = forms.CharField(widget=forms.Textarea, required=True)
    specialization = forms.ChoiceField(choices=SPECIALIZATION_CHOICES)  # Use ChoiceField for select input
    profile_pic = forms.ImageField(required=True)  # Include a profile picture field

    class Meta:
        model = models.Pharmacist
        fields = ['first_name', 'last_name', 'contact_email', 'contact_phone', 'license_number', 'address', 'specialization', 'profile_pic']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MedicineForm(forms.ModelForm):
    symptoms = forms.ModelMultipleChoiceField(queryset=models.Symptom.objects.all(), widget=forms.SelectMultiple)
    class Meta:
        model = models.Medicine
        fields = ['name', 'description', 'manufacturer', 'dosage', 'unit_price', 'quantity', 'expiry_date', 'category', 'profile_pic', 'symptoms']

    widgets = {
        'expiry_date': forms.DateInput(attrs={'type': 'date'}),
    }

    profile_pic = forms.ImageField(required=False)  # Include a profile picture field for medicine thumbnail

#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30, required=True)
    Email = forms.EmailField(required=True)
    Subject = forms.CharField(max_length=30, required=True)
    Message = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}), required=True)


