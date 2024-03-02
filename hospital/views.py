
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render,redirect
from django.urls import reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.hashers import make_password
from datetime import datetime,timedelta,date
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from . import forms
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from datetime import date


#   REST API Instances
from rest_framework import generics
from .serializers import PatientSerializer

class PatientListCreate(generics.ListCreateAPIView):
    serializer_class = PatientSerializer

    def get_queryset(self):
        # Check if the user is an admin 
        if self.request.user.groups.filter(name='ADMIN').exists():
            # Admins can access all patients
            return models.Patient.objects.all()
        else:
            return models.Patient.objects.none()

class PatientRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    
    def get_queryset(self):
        # Check if the user is an admin 
        if self.request.user.groups.filter(name='ADMIN').exists():
            # Admins can access all patients
            return models.Patient.objects.all()
        else:
            return models.Patient.objects.none()

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})

# Create your views here.
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/index.html')

def doctor_wait_for_approval(request):
    return render(request, 'hospital/doctor_wait_for_approval.html')

#for showing signup/login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/adminclick.html')


#for showing signup/login button for doctor(by sumit)
def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/doctorclick.html')


#for showing signup/login button for patient(by sumit)
def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/patientclick.html')

#Login Forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AdminLoginForm, DoctorForm, DoctorLoginForm, DoctorUserForm, PatientLoginForm, StaffAdminProfileForm, StaffAdminSignupForm

def adminlogin_view(request):
    form = AdminLoginForm()

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            print(f"Attempting login with username: {username}, password: {password}")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                print(f"User authentication successful for {username}")
                
                if is_admin(user):
                    login(request, user)
                    return redirect('afterlogin')
                else:
                    # User is not an admin or maybe a superuser
                    return redirect('superadmin')
            else:
                # Authentication failed
                messages.error(request, "Invalid username or password.")
        else:
            # This block is executed when the form is not valid
            print(f"Form is not valid. Form errors: {form.errors}")
            messages.error(request, "Invalid username or password. Please check the fields.")

    return render(request, 'hospital/adminlogin.html', {'form': form})

def doctorlogin_view(request):
    form = DoctorLoginForm()
    
    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None and is_doctor(user):
                login(request, user)
                return redirect('afterlogin')
            else:
                # Authentication failed
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid form submission. Please check the fields.")

    return render(request, 'hospital/doctorlogin.html', {'form': form})

def patientlogin_view(request):
    form = PatientLoginForm()
    if request.method == 'POST':
        form = PatientLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None and is_patient(user):
                login(request, user)
                return redirect('afterlogin')
            else:
                # Authentication failed
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid form submission. Please check the fields.")

    return render(request, 'hospital/patientlogin.html', {'form': form})
    
        
#SignUp Views

def staff_admin_signup_view(request):
    adminForm = StaffAdminSignupForm()
    profile_form = StaffAdminProfileForm()

    if request.method == 'POST':
        adminForm = StaffAdminSignupForm(request.POST)
        profile_form = StaffAdminProfileForm(request.POST, request.FILES)

        if adminForm.is_valid() and profile_form.is_valid():
            user = adminForm.save(commit=False)
            user.username = adminForm.cleaned_data['username']
            user.set_password(adminForm.cleaned_data['password1'])
            user.is_staff = True
            user.save()

            # Add user to 'ADMIN' group
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)

            # Create HospitalStaffAdmin instance
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.email = adminForm.cleaned_data['email']
            profile.mobile = profile_form.cleaned_data['mobile']
            profile.profile_pic = profile_form.cleaned_data['profile_pic']
            profile.save()

            
            messages.success(request, "User registered successfully!")
            return HttpResponseRedirect('adminlogin')
        else:
            for field, errors in adminForm.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"Profile {error}")

    return render(request, 'hospital/adminsignup.html', {'form': adminForm, 'profile_form': profile_form})

def doctor_signup_view(request):
    if request.method == 'POST':
        doctorForm = DoctorUserForm(request.POST)
        profile_form = DoctorForm(request.POST, request.FILES)

        if doctorForm.is_valid() and profile_form.is_valid():
            user = doctorForm.save(commit=False)
            user.username = doctorForm.cleaned_data['username']
            user.set_password(doctorForm.cleaned_data['password1'])
            user.save()

            # Create Doctor instance
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.email = doctorForm.cleaned_data['email']
            profile.mobile = profile_form.cleaned_data['mobile']
            

            # Check if profile pic is present in cleaned data
            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']

            profile.save()

            # Add user to 'DOCTOR' group
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
            
            messages.success(request, "User registered successfully!")
            return HttpResponseRedirect('doctorlogin')
        else:
            print("Doctor Form Errors:", doctorForm.errors)
            print("Profile Form Errors:", profile_form.errors)
            for field, errors in doctorForm.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"Profile {error}")
    else:
        doctorForm = DoctorUserForm()
        profile_form = DoctorForm()

    return render(request, 'hospital/doctorsignup.html', {'form': doctorForm, 'profile_form': profile_form})

#def doctor_signup_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST,request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor=doctor.save()
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
        return HttpResponseRedirect('doctorlogin')
    return render(request,'hospital/doctorsignup.html',context=mydict)

def patient_signup_view(request):
    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)

        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])  # Set password for the user
            user.save()
            
            patient = patientForm.save(commit=False)
            patient.user = user
            patient.status = False
            
            # Get the assigned doctor's ID from the form data
            assigned_doctor_id = request.POST.get('assigned_doctor_id')  # Correct variable name
            if assigned_doctor_id:
                assigned_doctor_id = int(assigned_doctor_id)  # Convert to integer
                try:
                    # Fetch the doctor object based on the ID
                    doctor = models.Doctor.objects.get(user_id=assigned_doctor_id)
                    patient.assigned_doctor_id = assigned_doctor_id
                    patient.assigned_doctor = str(doctor)
                    patient.admit_date = date.today()
                except models.Doctor.DoesNotExist:
                    messages.error(request, "Invalid doctor ID provided")
                    return render(request, 'hospital/patientsignup.html', {'userForm': userForm, 'patientForm': patientForm})
            
            patient.save()
            
            my_patient_group, created = Group.objects.get_or_create(name='PATIENT')
            my_patient_group.user_set.add(user)
            
            messages.success(request, "User Registered")
            return HttpResponseRedirect('patientlogin')
        else:
            for field, errors in userForm.errors.items():
                for error in errors:
                    messages.error(request, f"User Form: {field.capitalize()} - {error}")
            for field, errors in patientForm.errors.items():
                for error in errors:
                    messages.error(request, f"Patient Form: {field.capitalize()} - {error}")
    else:
        userForm = forms.PatientUserForm()
        patientForm = forms.PatientForm()

    context = {'userForm': userForm, 'patientForm': patientForm}
    return render(request, 'hospital/patientsignup.html', context)

#def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.assigned_doctor_id=request.POST.get('assigned_doctor_id')
            patient=patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request,'hospital/patientsignup.html',context=mydict)



#-----------for checking user is doctor , patient or admin
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()
def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,DOCTOR OR PATIENT

from django.urls import reverse
from django.http import HttpResponseRedirect

def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_doctor(request.user):
        account_approval = models.Doctor.objects.filter(user_id=request.user.id, status__in=[models.Doctor.STATUS_AVAILABLE, models.Doctor.STATUS_NOTAVAILABLE]).exists()
        if account_approval:
            return redirect('doctor-dashboard')
        else:
            return render(request, 'hospital/doctor_wait_for_approval.html')
    elif is_patient(request.user):
        account_approval = models.Patient.objects.filter(user_id=request.user.id, status=True).exists()
        if account_approval:
            return redirect('patient-dashboard')
        else:
            return render(request, 'hospital/patient_wait_for_approval.html')
    else:
        # Use the existing functions to determine the login type
        if is_patient(request.user):
            messages.error(request, "Invalid User or Password")
            return HttpResponseRedirect(reverse('patientlogin'))
        elif is_doctor(request.user):
            messages.error(request, "Invalid User or Password")
            return HttpResponseRedirect(reverse('doctorlogin'))
        elif is_admin(request.user):
            messages.error(request, "Invalid User or Password")
            return HttpResponseRedirect(reverse('adminlogin'))
        else:
            # Handle the case when the login type is unknown or not defined
            return HttpResponse("Unknown user type")
#---------------------------------------------------------------------------------
#------------------------ CHANGING PROFILE PIC -----------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_change_profile_pic(request):
    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')

        if profile_pic:
            try:
                staff = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
            except models.HospitalStaffAdmin.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'HospitalStaffAdmin does not exist for this user.'}, status=400)

            staff.profile_pic = profile_pic
            staff.save()
            return JsonResponse({'success': True})  # Optionally, return a JSON response indicating success

    return JsonResponse({'success': False})  # Return a JSON response indicating failure

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_change_profile_pic(request):
    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')

        if profile_pic:
            try:
                doctor = models.Doctor.objects.get(user_id=request.user.id)
            except models.Doctor.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Doctor does not exist for this user.'}, status=400)

            doctor.profile_pic = profile_pic
            doctor.save()
            return JsonResponse({'success': True})  # Optionally, return a JSON response indicating success

    return JsonResponse({'success': False})  # Return a JSON response indicating failure

@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_change_profile_pic(request):
    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')

        if profile_pic:
            try:
                patient = models.Patient.objects.get(user_id=request.user.id)
            except models.Patient.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Patient does not exist for this user.'}, status=400)

            patient.profile_pic = profile_pic
            patient.save()
            return JsonResponse({'success': True})  # Optionally, return a JSON response indicating success

    return JsonResponse({'success': False})  # Return a JSON response indicating failure


#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
from collections import Counter
from django.db.models import Q
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    
    #for both table in admin dashboard
    doctors=models.Doctor.objects.all().order_by('-id')
    patients=models.Patient.objects.all().order_by('-id')
    #for three cards
    doctorcount = models.Doctor.objects.filter(Q(status=models.Doctor.STATUS_AVAILABLE) | Q(status=models.Doctor.STATUS_NOTAVAILABLE)).count()
    pendingdoctorcount=models.Doctor.objects.all().filter(status=models.Doctor.STATUS_ONHOLD).count()

    patientcount=models.Patient.objects.all().filter(status=True).count()
    pendingpatientcount=models.Patient.objects.all().filter(status=False).count()
    patientadmitdate=models.Patient.objects.all()

    appointmentcount=models.Appointment.objects.all().filter(status=True).count()
    pendingappointmentcount=models.Appointment.objects.all().filter(status=False).count()
    
    admission_dates = [patient.admit_date for patient in patientadmitdate]
    admission_counts = Counter(admission_dates)

    # Convert admission_counts to a list of tuples (date, count)
    admission_counts_list = list(admission_counts.items())
    

    mydict={
    'doctors':doctors,
    'patients':patients,
    'doctorcount':doctorcount,
    'pendingdoctorcount':pendingdoctorcount,
    'patientcount':patientcount,
    'pendingpatientcount':pendingpatientcount,
    'patientadmitdate':patientadmitdate,
    'appointmentcount':appointmentcount,
    'pendingappointmentcount':pendingappointmentcount,
    'admission_counts_list': admission_counts_list,
    'admin':models.HospitalStaffAdmin.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/admin_dashboard.html',context=mydict)


# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    context = {
        'admin': admin,
    }
    return render(request,'hospital/admin_doctor.html', context)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=models.Doctor.STATUS_AVAILABLE)
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    context = {
        'admin': admin,
        'doctors': doctors
    }
    return render(request,'hospital/admin_view_doctor.html', context)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_doctor_view(request, pk):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)
    userForm = forms.DoctorUserForm(instance=user)
    doctorForm = forms.DoctorForm(request.FILES, instance=doctor)
    
    doctorForm.fields['address'].initial = doctor.get_address
    doctorForm.fields['mobile'].initial = doctor.get_mobile
    doctorForm.fields['department'].initial = doctor.get_department
    doctorForm.fields['license_num'].initial = doctor.get_licenseNum
    
    mydict = {'userForm': userForm, 'doctorForm': doctorForm, 'admin':admin,  }
    
    if request.method == 'POST':
        userForm = forms.UpdateDoctorUserForm(request.POST, instance=user)
        doctorForm = forms.UpdateDoctorForm(request.POST, request.FILES, instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user = userForm.save(commit=False)
            user.save()
            
            doctor = doctorForm.save(commit=False)
            doctor.department = doctor.address = doctorForm.cleaned_data['department']
            doctor.address = doctorForm.cleaned_data['address']
            doctor.mobile = doctorForm.cleaned_data['mobile']
            doctor.profile_pic = doctorForm.cleaned_data['profile_pic']
            doctor.status = 1
            doctor.save()
            return redirect('admin-view-doctor')
        else:
            print("User Form Errors:", userForm.errors)
            print("Doctor Form Errors:", doctorForm.errors)
            for field, errors in doctorForm.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            for field, errors in userForm.errors.items():
                for error in errors:
                    messages.error(request, f"UserProfile {error}")
    return render(request, 'hospital/admin_update_doctor.html', context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    doctorForm=forms.DoctorUserForm(request.POST)
    profile_form=forms.DoctorForm(request.POST or None, request.FILES)
    mydict={'form':doctorForm,'profile_form':profile_form, 'admin': admin}
    
    if request.method=='POST':
        doctorForm=forms.DoctorUserForm(request.POST)
        profile_form=forms.DoctorForm(request.POST or None, request.FILES)
        
        if doctorForm.is_valid() and profile_form.is_valid():
            user=doctorForm.save()
            user.username = doctorForm.cleaned_data['username']
            user.save()

            profile=profile_form.save(commit=False)
            profile.user=user
            profile.email = doctorForm.cleaned_data['email']
            profile.mobile = profile_form.cleaned_data['mobile']
            profile.profile_pic = profile_form.cleaned_data['profile_pic']
            profile.status= models.Doctor.STATUS_AVAILABLE
            profile.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
        
        else:
            for field, errors in doctorForm.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"Profile {error}")
        return redirect(reverse('admin-view-doctor'))
    else:
        doctorForm=forms.DoctorUserForm()
        profile_form=forms.DoctorForm()
       
    return render(request,'hospital/admin_add_doctor.html',context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    #those whose approval are needed
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    doctors=models.Doctor.objects.all().filter(status=models.Doctor.STATUS_ONHOLD)
    context = {
        'doctors':doctors,
        'admin': admin,
    }
    return render(request,'hospital/admin_approve_doctor.html', context)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    doctor.status= models.Doctor.STATUS_AVAILABLE
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_details_view(request, id):
    # Get the patient object
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    doctor = models.Doctor.objects.get(id=id)
    #doctor = get_object_or_404(models.Doctor, id=id)
    
    # Get the associated user object
    user = doctor.user
    
    # Prepare the context dictionary
    context = {
        "doctor": doctor,
        "user": user,
        "admin": admin,
    }

    return render(request, 'hospital/admin_doctor_details.html', context)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    staff = models.HospitalStaffAdmin.objects.all()
    doctors=models.Doctor.objects.all().filter(status=models.Doctor.STATUS_AVAILABLE)
    context = {
        'staff': staff,
        'admin': admin,
        'doctors': doctors,
    }
    return render(request,'hospital/admin_view_doctor_specialisation.html', context)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    context = {
        'admin': admin,
    }
    return render(request,'hospital/admin_patient.html', context)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    context = {
        'admin': admin,
        'patients': patients,
    }
    return render(request,'hospital/admin_view_patient.html', context)

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_details_view(request, patient_id):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    # Get the patient object
    patient = get_object_or_404(models.Patient, id=patient_id)
    
    # Get the associated user object
    user = patient.user
    
    # Get the insurance object related to the patient
    try:
        insurance = models.Insurance.objects.get(patient=patient)
    except models.Insurance.DoesNotExist:
        insurance = None
    
    # Prepare the context dictionary
    context = {
        "patient": patient,
        "user": user,
        "insurance": insurance,
        "admin": admin,
    }

    return render(request, 'hospital/admin_patient_details.html', context)

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_patient_view(request, pk):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    patient = models.Patient.objects.get(id=pk)
    user = models.User.objects.get(id=patient.user_id)

    userForm = forms.UpdatePatientUserForm(instance=user)
    patientForm = forms.UpdatePatientForm(instance=patient)

    # Set initial values for form fields
    patientForm.fields['address'].initial = patient.get_address
    patientForm.fields['mobile'].initial = patient.get_mobile
    patientForm.fields['date_of_birth'].initial = patient.get_DOB.strftime('%Y-%m-%d')
    patientForm.fields['gender'].initial = patient.get_gender
    patientForm.fields['symptoms'].initial = patient.get_symptoms
   
    if request.method == 'POST':
        userForm = forms.UpdatePatientUserForm(request.POST, instance=user)
        patientForm = forms.UpdatePatientForm(request.POST, request.FILES, instance=patient)

        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save()
            email = request.POST.get('email')
            user.email = email
            # Check if a new password is provided in the form
            new_password = request.POST.get('password')
            if new_password:
                # Set the new password
                user.set_password(new_password)
            user.save()

            patient = patientForm.save(commit=False)
            patient.status = True
            # Get the assigned doctor ID from the form data
            assigned_doctor_id = request.POST.get('assigned_doctor_id')
            doctor = models.Doctor.objects.get(user_id=assigned_doctor_id)
            print("Assigned Doctor ID:", assigned_doctor_id)
            if assigned_doctor_id:
                assigned_doctor_id = int(assigned_doctor_id)  # Convert to integer
                try:
                    # Fetch the doctor object based on the ID
                    patient.assigned_doctor_id = assigned_doctor_id
                    patient.assigned_doctor = str(doctor)
                except models.Doctor.DoesNotExist:
                    messages.error(request, "Invalid doctor ID provided")
                    return render(request, 'hospital/admin_update_patient.html', {'userForm': userForm, 'patientForm': patientForm})

            patient.save()
            messages.success(request, "Patient information updated successfully.")
            return redirect('admin-view-patient')
        else:
            for field, errors in userForm.errors.items():
                for error in errors:
                    messages.error(request, f"User Form: {field.capitalize()} - {error}")
            for field, errors in patientForm.errors.items():
                for error in errors:
                    messages.error(request, f"Patient Form: {field.capitalize()} - {error}")

    mydict = {'userForm': userForm, 'patientForm': patientForm, 'admin': admin,}
    return render(request, 'hospital/admin_update_patient.html', context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_patient_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    userForm = forms.PatientUserForm()
    patientForm = forms.UpdatePatientForm()
    context = {'userForm': userForm, 'patientForm': patientForm, 'admin': admin}
    
    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)
        
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()
            
            patient = patientForm.save(commit=False)
            patient.user = user
            patient.status = True  # Assuming status True for admin admission
            
            assigned_doctor_id = request.POST.get('assigned_doctor_id')
            
            if assigned_doctor_id:
                assigned_doctor_id = int(assigned_doctor_id)  # Convert to integer
                doctor = models.Doctor.objects.get(user_id= assigned_doctor_id)
                try:
                    # Fetch the doctor object based on the ID
                    patient.assigned_doctor_id = assigned_doctor_id
                    patient.assigned_doctor = str(doctor)
                except models.Doctor.DoesNotExist:
                    messages.error(request, "Invalid doctor ID provided")
                    return render(request, 'hospital/admin_add_patient.html', context=context)
            
            patient.save()
            
            my_patient_group, created = Group.objects.get_or_create(name='PATIENT')
            my_patient_group.user_set.add(user)
            
            messages.success(request, "Patient Registered Successfully")
            return HttpResponseRedirect('admin-view-patient')  # Adjust the URL path according to your project's URL configuration
        else:
            for field, errors in userForm.errors.items():
                for error in errors:
                    messages.error(request, f"User Form: {field.capitalize()} - {error}")
            for field, errors in patientForm.errors.items():
                for error in errors:
                    messages.error(request, f"Patient Form: {field.capitalize()} - {error}")

    # If the request method is GET or form validation fails, render the form again with the error messages
    return render(request, 'hospital/admin_add_patient.html', context=context)


#------------------FOR APPROVING PATIENT BY ADMIN----------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_patient_view(request):
    #those whose approval are needed
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    patients=models.Patient.objects.all().filter(status=False)
    context = {
        'patients': patients,
        'admin': admin
    }
    return render(request,'hospital/admin_approve_patient.html', context)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-patient'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')



#--------------------- FOR DISCHARGING PATIENT BY ADMIN START-------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_discharge_patient_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    patients=models.Patient.objects.all().filter(status=True)
    context = {
        'patients': patients,
        'admin': admin,
    }
    return render(request,'hospital/admin_discharge_patient.html', context)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def discharge_patient_view(request,pk):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    patient=models.Patient.objects.get(id=pk)
    days=(date.today()-patient.admit_date) #2 days, 0:00:00
    assignedDoctor=models.User.objects.all().filter(id=patient.assigned_doctor_id)
    d=days.days # only how many day that is 2
    patientDict={
        'patientId':pk,
        'name':patient.get_name,
        'mobile':patient.mobile,
        'address':patient.address,
        'symptoms':patient.symptoms,
        'admit_date':patient.admit_date,
        'todayDate':date.today(),
        'day':d,
        'assignedDoctorName':assignedDoctor[0].first_name,
        'admin': admin,
    }
    if request.method == 'POST':
        feeDict ={
            'roomCharge':int(request.POST['roomCharge'])*int(d),
            'doctorFee':request.POST['doctorFee'],
            'medicineCost' : request.POST['medicineCost'],
            'OtherCharge' : request.POST['OtherCharge'],
            'total':(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        }
        patientDict.update(feeDict)
        #for updating to database patientDischargeDetails (pDD)
        pDD=models.PatientDischargeDetails()
        pDD.patientId=pk
        pDD.patientName=patient.get_name
        pDD.assignedDoctorName=assignedDoctor[0].first_name
        pDD.address=patient.address
        pDD.mobile=patient.mobile
        pDD.symptoms=patient.symptoms
        pDD.admitDate=patient.admit_date
        pDD.releaseDate=date.today()
        pDD.daySpent=int(d)
        pDD.medicineCost=int(request.POST['medicineCost'])
        pDD.roomCharge=int(request.POST['roomCharge'])*int(d)
        pDD.doctorFee=int(request.POST['doctorFee'])
        pDD.OtherCharge=int(request.POST['OtherCharge'])
        pDD.total=(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        pDD.save()
        return render(request,'hospital/patient_final_bill.html',context=patientDict)
    return render(request,'hospital/patient_generate_bill.html',context=patientDict)



#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return



def download_pdf_view(request,pk):
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=pk).order_by('-id')[:1]
    dict={
        'patientName':dischargeDetails[0].patientName,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':dischargeDetails[0].address,
        'mobile':dischargeDetails[0].mobile,
        'symptoms':dischargeDetails[0].symptoms,
        'admitDate':dischargeDetails[0].admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
    }
    return render_to_pdf('hospital/download_bill.html',dict)



#-----------------APPOINTMENT START--------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    context = {'admin': admin,}
    return render(request,'hospital/admin_appointment.html', context)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments=models.Appointment.objects.all().filter(status=models.Appointment.ACCEPTED)
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    context = {
        'admin': admin,
        'appointments':appointments,   
    }
    return render(request,'hospital/admin_view_appointment.html', context)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    appointmentForm=forms.AppointmentForm()
    mydict={'appointmentForm':appointmentForm, 'admin': admin}
    if request.method=='POST':
        appointmentForm=forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.POST.get('patientId')
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=models.User.objects.get(id=request.POST.get('patientId')).first_name
            appointment.status= models.Appointment.ACCEPTED
            appointment.save()
        return HttpResponseRedirect('admin-view-appointment')
    return render(request,'hospital/admin_add_appointment.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=models.Appointment.PENDING)
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    context = {'admin': admin,
               'appointments':appointments,
    }
    return render(request,'hospital/admin_approve_appointment.html', context)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(appointment_id=pk)
    appointment.status= models.Appointment.ACCEPTED
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(appointment_id=pk)
    appointment.status = models.Appointment.REJECTED
    appointment.save()
    return redirect('admin-approve-appointment')
#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    #for three cards
    patientcount=models.Patient.objects.all().filter(status=True,assigned_doctor_id=request.user.id).count()
    appointmentcount=models.Appointment.objects.all().filter(status=models.Appointment.ACCEPTED ,doctorId=request.user.id).count()
    patientdischarged=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name).count()

    #for table in doctor dashboard
    appointments=models.Appointment.objects.all().filter(status=models.Appointment.ACCEPTED,doctorId=request.user.id).order_by('-appointment_id')
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_dashboard.html',context=mydict)


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_toggle_availability(request):
    if request.method == 'POST':
        doctor = models.Doctor.objects.get(user_id=request.user.id)
        doctor.toggle_availability()
        return JsonResponse({'success': True})  # Optionally, return a JSON response indicating success
    else:
        return JsonResponse({'success': False})  # Optionally, return a JSON response indicating Failed
    
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict={
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_patient.html',context=mydict)


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True,assigned_doctor_id=request.user.id)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    dischargedpatients=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_view_discharge_patient.html',{'dischargedpatients':dischargedpatients,'doctor':doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_appointment.html',{'doctor':doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=models.Appointment.ACCEPTED,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_view_appointment.html',{'appointments':appointments,'doctor':doctor})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_approve_appointment_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(status=models.Appointment.PENDING, doctorId=doctor.get_id)
    return render(request, 'hospital/doctor_approve_appointment.html', {'appointments': appointments, 'doctor': doctor})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def approve_doctor_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(appointment_id=pk)
    appointment.status= models.Appointment.ACCEPTED
    appointment.save()
    return redirect(reverse('doctor-approve-appointment'))



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def reject_doctor_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(appointment_id=pk)
    appointment.status= models.Appointment.REJECTED
    appointment.save()
    return redirect('doctor-approve-appointment')


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_add_appointment_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    doctor_patients = models.Patient.objects.filter(status=True, assigned_doctor_id=request.user.id)

    if request.method == 'POST':
        appointmentForm = forms.DoctorAppointmentForm(request.POST, doctor_patients=doctor_patients)
        if appointmentForm.is_valid():
            appointment = appointmentForm.save(commit=False)
            appointment.doctorId = request.user.id

            # Get the patient based on the selected user_id from the form
            patient_id = request.POST.get('patientId')
            patient = models.Patient.objects.get(user_id=patient_id)

            appointment.patientId = patient_id
            appointment.doctorName = request.user.get_full_name()
            appointment.patientName = patient.get_name
            appointment.status = models.Appointment.ACCEPTED
            appointment.save()
            messages.success(request, 'Appointment booked successfully!')
            return HttpResponseRedirect('doctor-view-appointment')
        else:
            for field, errors in appointmentForm.errors.items():
                for error in errors:
                    messages.error(request, f"Appointment Form: {field.capitalize()} - {error}")
    else:
        appointmentForm = forms.DoctorAppointmentForm(doctor_patients=doctor_patients)

    mydict = {'appointmentForm': appointmentForm, 'doctor': doctor}
    return render(request, 'hospital/doctor_add_appointment.html', context=mydict)


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_set_status_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=models.Appointment.ACCEPTED,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=models.Appointment.ACCEPTED,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_status_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def set_complete_appointment_view(request, pk):
    appointment = models.Appointment.objects.get(appointment_id=pk)
    
    if appointment.ACCEPTED:
        appointment.status = models.Appointment.COMPLETED
        appointment.save()
    else:
        # Delete appointment if set completed
        appointment.delete()
    
    doctor = models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments = models.Appointment.objects.filter(status=models.Appointment.COMPLETED, doctorId=request.user.id)
    patientids = appointments.values_list('patientId', flat=True)
    patients = models.Patient.objects.filter(status=True, user_id__in=patientids)
    appointments = zip(appointments, patients)
    
    return render(request, 'hospital/doctor_delete_appointment.html', {'appointments': appointments, 'doctor': doctor})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_details_view(request, patient_id):
    # Get the patient object
    patient = get_object_or_404(models.Patient, id=patient_id)
    # Get the doctor object
    doctor = get_object_or_404(models.Doctor, user=request.user)
    
    # Ensure that the patient is assigned to the requesting doctor
    if patient.assigned_doctor_id != request.user.id:
        # Return a 403 Forbidden response or redirect to an appropriate page
        return HttpResponseForbidden("You are not authorized to view this patient's details.")
    
    # Get the associated user object
    user = patient.user
    
    # Get the insurance object related to the patient
    try:
        insurance = models.Insurance.objects.get(patient=patient)
    except models.Insurance.DoesNotExist:
        insurance = None
    
    # Prepare the context dictionary
    context = {
        "patient": patient,
        "user": user,
        "doctor": doctor,
        "insurance": insurance,
    }

    return render(request, 'hospital/doctor_patient_details.html', context)

#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ PATIENT RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    doctor = models.Doctor.objects.get(user_id=patient.assigned_doctor_id)
    try:
        appointment = models.Appointment.objects.get(patientId=request.user.id)
        appointment_date = appointment.appointmentDate.strftime("%b. %d, %Y %I:%M %p")
        appointment_status = appointment.status
    except models.Appointment.DoesNotExist:
        appointment_date = None
        appointment_status = None

    mydict = {
        'patient': patient,
        'doctorName': doctor.get_name,
        'doctorMobile': doctor.mobile,
        'doctorAddress': doctor.address,
        'doctorAvailability': doctor.status,
        'symptoms': patient.symptoms,
        'doctorDepartment': doctor.department,
        'admit_date': patient.admit_date,
        'appointmentDate': appointment_date,
        'appointmentStatus': appointment_status,
    }
    return render(request, 'hospital/patient_dashboard.html', context=mydict)

@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_appointment.html',{'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    doctor=models.Doctor.objects.get(user_id=patient.assigned_doctor_id)
    assigned_doctor_id = patient.assigned_doctor_id
    patient_doctors = models.Doctor.objects.filter(status=True, user_id = assigned_doctor_id)
    appointmentForm=forms.PatientAppointmentForm(patient_doctors=patient_doctors)

    message=None
    mydict={
        'appointmentForm':appointmentForm,
        'patient':patient,
        'message':message,
        }
    
    if request.method=='POST':
        appointmentForm=forms.PatientAppointmentForm(request.POST, patient_doctors=patient_doctors)
        if appointmentForm.is_valid():
            print(request.POST.get('doctorId'))
            desc=request.POST.get('description')

            doctor=models.Doctor.objects.get(user_id=request.POST.get('doctorId'))
            
            if doctor.department == 'Cardiologist':
                if 'heart' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request,'hospital/patient_book_appointment.html',{'appointmentForm':appointmentForm,'patient':patient,'message':message})


            if doctor.department == 'Dermatologists':
                if 'skin' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request,'hospital/patient_book_appointment.html',{'appointmentForm':appointmentForm,'patient':patient,'message':message})

            if doctor.department == 'Emergency Medicine Specialists':
                if 'fever' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request,'hospital/patient_book_appointment.html',{'appointmentForm':appointmentForm,'patient':patient,'message':message})

            if doctor.department == 'Allergists/Immunologists':
                if 'allergy' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request,'hospital/patient_book_appointment.html',{'appointmentForm':appointmentForm,'patient':patient,'message':message})

            if doctor.department == 'Anesthesiologists':
                if 'surgery' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request,'hospital/patient_book_appointment.html',{'appointmentForm':appointmentForm,'patient':patient,'message':message})

            if doctor.department == 'Colon and Rectal Surgeons':
                if 'cancer' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request,'hospital/patient_book_appointment.html',{'appointmentForm':appointmentForm,'patient':patient,'message':message})

            if doctor.department == 'Gastroenterologists':
                if 'digestive' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})

            if doctor.department == 'Hematologists':
                if 'blood' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})

            if doctor.department == 'Nephrologists':
                if 'kidney' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})

            if doctor.department == 'Neurologists':
                if 'nerve' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})

            if doctor.department == 'Oncologists':
                if 'cancer' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})

            if doctor.department == 'Ophthalmologists':
                if 'eye' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})

            if doctor.department == 'Orthopedic Surgeons':
                if 'bone' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})

            if doctor.department == 'Pediatricians':
                if 'child' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})

            if doctor.department == 'Psychiatrists':
                if 'mental' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})

            if doctor.department == 'Radiologists':
                if 'radiology' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})

            if doctor.department == 'Rheumatologists':
                if 'joint' in desc:
                    pass
                else:
                    print('else')
                    messages.error=(request,"Please Choose Doctor According To Disease")
                    return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})
    

            doctor = User.objects.get(id=request.POST.get('doctorId'))
            patient = User.objects.get(id=request.user.id)
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.user.id #----user can choose any patient but only their info will be stored
            appointment.doctorName= f"{doctor.first_name} {doctor.last_name}"
            appointment.patientName= f"{patient.first_name} {patient.last_name}"
            appointment.status= 0 # Pending(Request)
            appointment.save()
        return HttpResponseRedirect('patient-view-appointment')
    else:
        # If it's a GET request, just initialize the form with the filtered queryset
        appointmentForm = forms.PatientAppointmentForm(patient_doctors=patient_doctors)
    
    return render(request,'hospital/patient_book_appointment.html',context=mydict)



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    appointments=models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request,'hospital/patient_view_appointment.html',{'appointments':appointments,'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=patient.id).order_by('-id')[:1]
    patientDict=None
    if dischargeDetails:
        patientDict ={
        'is_discharged':True,
        'patient':patient,
        'patientId':patient.id,
        'patientName':patient.get_name,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':patient.address,
        'mobile':patient.mobile,
        'symptoms':patient.symptoms,
        'admit_date':patient.admit_date,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
        }
    else:
        patientDict={
            'is_discharged':False,
            'patient':patient,
            'patientId':request.user.id,
        }
    return render(request,'hospital/patient_discharge.html',context=patientDict)

@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_insurance_view(request):
    # Get the patient associated with the current user
    patient = get_object_or_404(models.Patient, user=request.user)
    
    if request.method == 'POST':
        insurance_instance = get_object_or_404(models.Insurance, patient=patient)
        insurance_form = forms.InsuranceForm(request.POST, instance=insurance_instance)
        if insurance_form.is_valid():
            # Save the updated insurance details
            insurance_form.save()
            messages.success(request, 'Insurance details updated successfully!')
            return redirect('patient-insurance')
    else:
        # Try to get the insurance instance for the patient
        insurance_instance = models.Insurance.objects.filter(patient=patient).first()
        if insurance_instance:
            # If insurance details exist, populate the form with the instance
            insurance_form = forms.InsuranceForm(instance=insurance_instance)
        else:
            # If no insurance details exist, create a new form
            insurance_form = forms.InsuranceForm()

    return render(request, 'hospital/patient_insurance.html', {'insuranceForm': insurance_form, 'patient': patient})

#------------------------ PATIENT RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------








#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START ------------------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'hospital/aboutus.html')

from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)
@csrf_exempt

def contactus_view(request):
    if request.method == 'POST':
        form = forms.ContactusForm(request.POST)

        if form.is_valid():
            user_name = form.cleaned_data['Name']
            user_email = form.cleaned_data['Email']
            subject = form.cleaned_data['Subject']
            message = form.cleaned_data['Message']

            try:
                # Inside the 'try' block
                send_mail(
                    f"{user_name} || <{user_email}> - {subject}",
                    message,
                    settings.EMAIL_HOST_USER,
                    settings.EMAIL_RECEIVING_USER,
                    fail_silently=False,
                )
                messages.success(request, 'Your feedback has been sent successfully.')
                return redirect('contactussuccess')
            except Exception as e:
                # Inside the 'except' block
                logger.error('An error occurred while sending feedback: %s', e)
                messages.error(request, 'An error occurred while sending your feedback. Please try again later.')
                # Log the error or handle it as needed
    else:
        form = forms.ContactusForm()
    # Outside the 'if request.method == 'POST':' block
    return render(request, 'hospital/contactus.html', {'form': form})

def contactussuccess(request):
    return render(request,'hospital/contactussuccess.html')



#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------

