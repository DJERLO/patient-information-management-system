import json
import random
import time
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render,redirect
from django.urls import reverse
from requests import Response
from . import forms,models
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.hashers import make_password
from datetime import datetime,timedelta,date
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from . import forms
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from datetime import date
from django.db.models import Max
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.paginator import Paginator

import requests
import base64
from dotenv import load_dotenv


#   REST API Instances
from rest_framework import generics, status
from rest_framework.views import APIView
from .serializers import PatientSerializer
from rest_framework.response import Response

from .departments import SPECIALIZATION_CHOICES, departments

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
        
class DoctorDepartmentListView(APIView):
    def get(self, request):
        return Response(departments)

class PharmacistSpecializationListView(APIView):
    def get(self, request):
        return Response(SPECIALIZATION_CHOICES)


#----End Of API instances
@csrf_exempt
def chatgpt4(request):
    if request.method == 'POST':
        user_message = request.POST.get('userMessage')

        url = "https://open-ai21.p.rapidapi.com/conversationgpt35"
        payload = {
            "messages": [
                {
                    "role": "patient",       # Patient
                    "content": user_message,  #  the user_message is sent as form data
                }
            ],
            "web_access": False, #This attribute is a boolean flag that indicates whether the model can interact with the database via the web.
            "system_prompt": "Hello! Welcome to our healthcare virtual agent. My name is Dr. Carey, Your healthcare virtual agent for today and I'm here to assist you with any questions or concerns you may have about your health. Feel free to ask me about symptoms, medications, treatment options, or any other healthcare-related topics. So How can I assist you today?",
            "temperature": 0.9, # This parameter controls the randomness of the generated responses.
            "top_k": 5,
            "top_p": 0.9,
            "max_tokens": 256, #This attribute sets the maximum number of tokens (words) in the generated response.
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "cf030a6d5amsh9fa16951e9dc229p1d1b96jsn60d40e50e951",
            'X-RapidAPI-Host': 'open-ai21.p.rapidapi.com'
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            print(response.json())
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()
            reply = data.get('result') #ChatGPT response result
            message = data.get('message') #429 Client Error

            if reply:
                return JsonResponse({'reply': reply}, status=200)
            
            if message:
                return JsonResponse({'reply': 'Error: Too many request at the moment'}, status=429)
        
        except requests.RequestException as e:
            return JsonResponse({'error': 'Failed to process message: {}'.format(str(e))}, status=500)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred: {}'.format(str(e))}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

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

#for showing signup/login button for admin
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/adminclick.html')

#for showing signup/login button for doctor
def receptionistclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/receptionistclick.html')

#for showing signup/login button for doctor
def pharmacistclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/pharmacistclick.html')

#for showing signup/login button for doctor
def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/doctorclick.html')


#for showing signup/login button for patient
def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/patientclick.html')

#Login Forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AdminLoginForm, DoctorForm, DoctorLoginForm, DoctorUserForm, PatientLoginForm, StaffAdminProfileForm, StaffAdminSignupForm, PharmacistUserSignUpForm, PharmacistSignUpForm
import logging
def adminlogin_view(request):
    form = AdminLoginForm()

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            print(f"Attempting login with username: {username}")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if is_pharmacist(user):
                    print("User is a pharmacist.")
                else:
                    print("User is not a pharmacist.")
                
                # Check if the user is an admin or a pharmacist
                if is_admin(user) or is_pharmacist(user):
                    login(request, user)
                    return redirect('afterlogin')
                else:
                    # If neither admin nor pharmacist, authentication fails
                    messages.error(request, "You are not authorized to access this page.")
            else:
                # Authentication failed
                messages.error(request, "Invalid username or password.")
        else:
            # This block is executed when the form is not valid
            print(f"Form is not valid. Form errors: {form.errors}")
            logger.error(f"Form is not valid. Form errors: {form.errors}")
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
                messages.error(request, "Authentication failed. Please contact the hospital management team for assistance with your account")
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

def pharmacist_signup_view(request):
    if request.method == 'POST':
        user_form = PharmacistUserSignUpForm(request.POST)
        profile_form = PharmacistSignUpForm(request.POST, request.FILES)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if user_form.is_valid() and profile_form.is_valid():
            
            user = user_form.save(commit=False)
            user.is_pharmacist = True
            user.save()

            pharmacist = profile_form.save(commit=False)
            pharmacist.user = user
            pharmacist.first_name = first_name
            pharmacist.last_name = last_name
            
            # Add user to 'PHARMACIST' group
            my_pharmacist_group = Group.objects.get_or_create(name='PHARMACIST')
            my_pharmacist_group.user_set.add(user)
            
            pharmacist.save()
            return HttpResponseRedirect('adminlogin')
    else:
        user_form = PharmacistUserSignUpForm()
        profile_form = PharmacistSignUpForm()
    return render(request, 'hospital/pharmacistsignup.html', {'user_form': user_form, 'profile_form': profile_form})

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

def patient_signup_view(request):
    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)

        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password1'])  # Set password for the user
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


#-----------for checking user is doctor , patient or admin
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_pharmacist(user):
    return user.groups.filter(name='PHARMACIST').exists()
def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()
def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()
def is_superuser(user):
    return user.is_superuser

#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,DOCTOR OR PATIENT

from django.urls import reverse
from django.http import HttpResponseRedirect

def afterlogin_view(request):
    if is_admin(request.user):
        account_approval = models.HospitalStaffAdmin.objects.filter(user_id=request.user.id, status=True).exists()
        if account_approval:
            return redirect('admin-dashboard')
        else:
            # Sending email notification to admin for account approval
            admin_email = request.user.email
            subject = 'Account Approval Required'
            message = 'Your account is awaiting approval. Please wait for the administrator to approve your account. \n\nBest Regards: The Hospital Management'
            from_email = settings.EMAIL_HOST_USER  # Update with your sender email
            to = [admin_email]
            send_mail(subject, message, from_email, to)

            return render(request, 'hospital/admin_wait_for_approval.html')
    elif is_pharmacist(request.user):
        account_approval = models.Pharmacist.objects.filter(user_id=request.user.id, status=True).exists()
        if account_approval:
            return redirect('pharmacist-dashboard')
        else:
            # Handle the case when the pharmacist account is not approved
            # You can render a template or return an appropriate response
            return render(request, 'hospital/pharmacist_wait_for_approval.html')
    elif is_doctor(request.user):
        account_approval = models.Doctor.objects.filter(user_id=request.user.id, status__in=[models.Doctor.STATUS_AVAILABLE, models.Doctor.STATUS_NOTAVAILABLE]).exists()
        if account_approval:
            return redirect('doctor-dashboard')
        else:
            # Sending email notification to doctor for account approval
            doctor_email = request.user.email
            subject = 'Account Approval Required'
            message = 'Your  account is awaiting approval Doctor. Please wait for the administrator to approve your account. \n\nBest Regards: The Hospital Management'
            from_email = settings.EMAIL_HOST_USER  # Update with your sender email
            to = [doctor_email]
            send_mail(subject, message, from_email, to)
            
            return render(request, 'hospital/doctor_wait_for_approval.html')
    elif is_patient(request.user):
        account_approval = models.Patient.objects.filter(user_id=request.user.id, status=True).exists()
        if account_approval:
            return redirect('patient-dashboard')
        else:
            # Sending email notification to patient for account approval
            patient_email = request.user.email
            subject = 'Account Approval Required'
            message = 'Your account is awaiting approval. Please wait for the administrator to approve your account.\n\nBest Regards: The Hospital Management'
            from_email = settings.EMAIL_HOST_USER  # Update with your sender email
            to = [patient_email]
            send_mail(subject, message, from_email, to)

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
        elif is_pharmacist(request.user):
            messages.error(request, "Invalid User or Password")
            return HttpResponseRedirect(reverse('adminlogin'))
        else:
            # Handle the case when the login type is unknown or not defined
            return HttpResponse("Unknown user type")
        
#--------LOGOUT VIEW
#Logout View
def logout_view(request):
    if is_admin(request.user):
        logout(request)  # Log out the current user
        return redirect('adminlogin')
    elif is_pharmacist(request.user):
        logout(request)  # Log out the current user
        return redirect('adminlogin')
    elif is_doctor(request.user):
        logout(request)  # Log out the current user
        return redirect('doctorlogin')
    elif is_patient(request.user):
        logout(request)  # Log out the current user
        return redirect('patientlogin')
    else:
        logout(request)  # Log out the current user
        return redirect('')

#---------------------------------------------------------------------------------
#------------------------ User Settings VIEW -------------------------------------
#---------------------------------------------------------------------------------
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_update_profile_details(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        
        user = User.objects.get(id=user_id)
        try:
            staff = models.HospitalStaffAdmin.objects.get(user_id = user_id)
        except models.HospitalStaffAdmin.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'HospitalStaffAdmin does not exist for this user.'}, status=400)

         # Update first name if changed
        if first_name:
            user.first_name = first_name

        # Update first name if changed
        if last_name:
            user.last_name = last_name

        # Update username if changed
        if username:
            user.username = username

        # Update password if changed
        if password:
            user.set_password(password)
            update_session_auth_hash(request, user)  # Keep the user logged in after password change

        # Email Change
        if email:
            user.email = email
        
        if mobile:
            staff.mobile = mobile
            staff.save()

        if address:
            staff.address = address
            staff.save()

        # Update profile picture if changed
        if profile_pic:
            staff.profile_pic = profile_pic
            staff.save()

        # Save the user object after all changes
        user.save()

        return JsonResponse({'success': True, 'message': 'Your details have been successfully updated.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@login_required(login_url='adminlogin')
@user_passes_test(is_pharmacist)
def pharmacist_update_profile_details(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        userEmail = request.POST.get('email1')
        workEmail = request.POST.get('email2')
        specialization = request.POST.get('specialization')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        
        user = User.objects.get(id=user_id)
        try:
            staff = models.Pharmacist.objects.get(user_id = user_id)
        except models.Pharmacist.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pharmacist does not exist for this user.'}, status=400)

         # Update first name if changed
        if first_name:
            user.first_name = first_name

        # Update first name if changed
        if last_name:
            user.last_name = last_name

        # Update username if changed
        if username:
            user.username = username

        # Update password if changed
        if password:
            user.set_password(password)
            update_session_auth_hash(request, user)  # Keep the user logged in after password change

        # Email Change
        if userEmail:
            user.email = userEmail

        # Work Email Change
        if workEmail:
            staff.contact_email = workEmail
            staff.save()
       
        if mobile:
            staff.contact_phone = mobile
            staff.save()

        if specialization:
            staff.specialization = specialization
            staff.save()

        if address:
            staff.address = address
            staff.save()

        # Update profile picture if changed
        if profile_pic:
            staff.profile_pic = profile_pic
            staff.save()

        # Save the user object after all changes
        user.save()

        return JsonResponse({'success': True, 'message': 'Your details have been successfully updated.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_update_profile(request):
    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        department = request.POST.get('department')
        license_num = request.POST.get('license_num')

        try:
            doctor = models.Doctor.objects.get(user_id=request.user.id)
        except models.Doctor.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Doctor does not exist for this user.'}, status=400)
        
        user = User.objects.get(id = request.user.id)

        #User
        if first_name:
            user.first_name = first_name

        if last_name:
            user.last_name = last_name
        
        if username:
            user.username = username

        if email:
            user.email = email
        
        if password:
            user.set_password(password)
            update_session_auth_hash(request, user) # Keep the user logged in after password change         

        #Doctor
        if profile_pic:
            doctor.profile_pic = profile_pic
            doctor.save()

        if address:
            doctor.address = address
            doctor.save()
        
        if mobile:
            doctor.mobile = mobile
            doctor.save()

        if department:
            doctor.department = department
            doctor.save()
        
        if license_num:
            doctor.license_num = license_num
            doctor.save()

        #User Record Save
        user.save()
        

        return JsonResponse({'success': True, 'message': 'Profile details updated successfully.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_update_profile_details(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        DOB = request.POST.get('DOB')
        
        user = User.objects.get(id=user_id)
        try:
            patient = models.Patient.objects.get(user_id=user_id)
        except models.Patient.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Patient does not exist for this user.'}, status=400)

        # Update first name if changed
        if first_name:
            user.first_name = first_name

        # Update last name if changed
        if last_name:
            user.last_name = last_name

        # Update username if changed
        if username:
            user.username = username

        # Update password if changed
        if password:
            user.set_password(password)
            update_session_auth_hash(request, user)  # Keep the user logged in after password change

        # Email Change
        if email:
            user.email = email
        
        if mobile:
            patient.mobile = mobile
            patient.save()

        if address:
            patient.address = address
            patient.save()
        
        if DOB:
            patient.date_of_birth = DOB
            patient.save()

        if gender:
            patient.gender = gender
            patient.save()

        # Update profile picture if changed
        if profile_pic:
            patient.profile_pic = profile_pic

        # Save the user and patient objects after all changes
        user.save()
        

        return JsonResponse({'success': True, 'message': 'Your details have been successfully updated.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})


#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
from collections import Counter

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    #for both table in admin dashboard and make sure their accounts is active
    doctors = models.Doctor.objects.filter(user__is_active=True).order_by('-id')
    patients = models.Patient.objects.filter(user__is_active=True).order_by('-id')
    #for three cards
    doctorcount = models.Doctor.objects.filter(Q(status=models.Doctor.STATUS_AVAILABLE) | Q(status=models.Doctor.STATUS_NOTAVAILABLE)).count()
    pendingdoctorcount=models.Doctor.objects.all().filter(status=models.Doctor.STATUS_ONHOLD).count()

    patientcount=models.Patient.objects.all().filter(Q(status=True)|Q(status=False)).count()
    admittedpatientcount =  models.Patient.objects.all().filter(status=True).count()
    pendingpatientcount=models.Patient.objects.all().filter(status=False).count()
    patientadmitdate=models.Patient.objects.all()

    appointmentcount=models.Appointment.objects.all().filter(Q(status=models.Appointment.ACCEPTED)|Q(status=models.Appointment.PENDING)|Q(status=models.Appointment.COMPLETED)).count()
    acceptedappointmentcount=models.Appointment.objects.all().filter(status=models.Appointment.ACCEPTED).count()
    pendingappointmentcount=models.Appointment.objects.all().filter(status=models.Appointment.PENDING).count()
    completedappointmentcount=models.Appointment.objects.all().filter(status=models.Appointment.COMPLETED).count()
    
    
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
    'admittedpatientcount': admittedpatientcount,
    'pendingpatientcount':pendingpatientcount,
    'patientadmitdate':patientadmitdate,
    'appointmentcount':appointmentcount,
    'pendingappointmentcount':pendingappointmentcount,
    'acceptedappointmentcount': acceptedappointmentcount,
    'completedappointmentcount':completedappointmentcount,
    'admission_counts_list': admission_counts_list,
    'admin':models.HospitalStaffAdmin.objects.get(user_id=request.user.id), #for profile picture of admin in sidebar
    }
    return render(request,'hospital/admin_dashboard.html',context=mydict)

# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
@user_passes_test(is_superuser)
def admin_panel_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    admins = models.HospitalStaffAdmin.objects.all().filter(status=True)
    pharmacist = models.Pharmacist.objects.all().filter(status=True)
    context = {
        'admin': admin,
        'admins': admins,
        'pharmacist': pharmacist,
    }
    return render(request,'hospital/admin_panel.html', context)


login_required(login_url='adminlogin')
@user_passes_test(is_superuser)
def admin_view_staff(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    admins = models.HospitalStaffAdmin.objects.all().filter(status=True)
    pharmacist = models.Pharmacist.objects.all().filter(status=True)
    context = {
        'admin': admin,
        'admins': admins,
        'pharmacist': pharmacist,
    }
    return render(request,'hospital/admin_view_staff.html', context)

@login_required(login_url='adminlogin')
@user_passes_test(is_superuser)
def admin_staff_details_view(request, pk):
    # Check if the user is a pharmacist or not
    is_pharmacist = models.Pharmacist.objects.filter(user_id=pk).exists()

    # Get the pharmacist or admin object based on the user's role
    if is_pharmacist:
        staff = models.Pharmacist.objects.get(user_id=pk)
    else:
        staff = models.HospitalStaffAdmin.objects.get(user_id=pk)

    # Check if the user is a superuser (admin)
    is_Admin = staff.user.is_superuser
    
    # Get the current admin
    admin = get_object_or_404(models.HospitalStaffAdmin, user_id=request.user.id)
    
    # Prepare the context dictionary
    context = {
        "admin": admin,
        "staff": staff,
        "is_Pharmacist": is_pharmacist,
        "is_Admin": is_Admin
    }

    return render(request, 'hospital/admin_staff_details.html', context)

@login_required(login_url='adminlogin')
@user_passes_test(is_superuser)
def approve_staff_view(request, pk):
    try:
        # Check if the user is a pharmacist or a receptionist
        pharmacist = models.Pharmacist.objects.get(user_id=pk)
        is_pharmacist = True
    except models.Pharmacist.DoesNotExist:
        is_pharmacist = False

    try:
        staff = models.HospitalStaffAdmin.objects.get(user_id=pk)
        is_staff = True
    except models.HospitalStaffAdmin.DoesNotExist:
        is_staff = False

    if is_pharmacist:
        # User is a pharmacist
        pharmacist.status = True
        pharmacist.save()
        user = pharmacist.user
    elif is_staff:
        # User is a receptionist or admin
        staff.status = True
        staff.save()
        user = staff.user
    else:
        # User is not a pharmacist or staff
        return HttpResponse("User not found or invalid")

    # Send approval email
    user_email = user.email
    subject = 'Staff Membership Approval: Hospital Management System'
    message = f'Hello,\n\nWe are pleased to inform you that you have been approved as a staff member on our Hospital Management System.\n\nYou now have access to all the tools and resources necessary to contribute effectively to our team.\n\nWelcome aboard, and thank you for joining us!\n\nBest regards,\nThe Hospital Management Team'
    sender_email = settings.EMAIL_HOST_USER
    receiver_email = [user_email]
    send_mail(subject, message, sender_email, receiver_email)

    return redirect(reverse('admin-approve-staff'))

@login_required(login_url='adminlogin')
@user_passes_test(is_superuser)
def delete_staff_view(request, pk):
    try:
        # Check if the user is a pharmacist or a receptionist
        pharmacist = models.Pharmacist.objects.get(user_id=pk)
        is_pharmacist = True
    except models.Pharmacist.DoesNotExist:
        is_pharmacist = False

    try:
        staff = models.HospitalStaffAdmin.objects.get(user_id=pk)
        is_staff = True
    except models.HospitalStaffAdmin.DoesNotExist:
        is_staff = False

    if is_pharmacist:
        # User is a pharmacist
        user = pharmacist.user
        pharmacist.delete()
    elif is_staff:
        # User is a receptionist
        user = staff.user
        staff.delete()
    else:
        # User is not a pharmacist or staff
        return HttpResponse("User not found or invalid")

    # Send rejection email
    user_email = user.email
    subject = 'Staff Membership Rejection: Hospital Management System'
    message = f'Hello,\n\nWe regret to inform you that your request to join as a staff member on our Hospital Management System has been rejected.\n\nIf you have any questions or require further clarification regarding this decision, please feel free to reach out to us.\n\nThank you for your interest.\n\nBest regards,\nThe Hospital Management Team'
    sender_email = settings.EMAIL_HOST_USER
    receiver_email = [user_email]
    send_mail(subject, message, sender_email, receiver_email)

    user.delete()
    return redirect('admin-view-staff')

@login_required(login_url='adminlogin')
@user_passes_test(is_superuser)
def admin_approve_staff_view(request):
    #those whose approval are needed
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    admins=models.HospitalStaffAdmin.objects.all().filter(status=False)
    pharmacist = models.Pharmacist.objects.all().filter(status=False)
    context = {
        'admins':admins,
        'pharmacist': pharmacist,
        'admin': admin,
    }
    return render(request,'hospital/admin_approve_staff.html', context)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=models.Doctor.STATUS_AVAILABLE)
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    context = {
        'admin': admin,
        'doctors': doctors,
    }
    return render(request,'hospital/admin_doctor.html', context)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=models.Doctor.STATUS_AVAILABLE)
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    context = {
        'admin': admin,
        'doctors': doctors,
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
def admin_doctor_details_view(request, id):
    # Get the patient object
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)

    doctor = get_object_or_404(models.Doctor, id=id)
    
    # Get the associated user object
    
    # Prepare the context dictionary
    context = {
        "doctor": doctor,
        "admin": admin,
    }

    return render(request, 'hospital/admin_doctor_details.html', context)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request,pk):
    doctor = models.Doctor.objects.get(id=pk)
    doctor.status = models.Doctor.STATUS_AVAILABLE
    doctor.save()

    # Send approval email
    user_email = doctor.user.email
    subject = 'Doctor Approval: Hospital Management System'
    message = f'Hello,\n\nCongratulations! You have been approved as a {doctor.department} on our Hospital Management System.\n\nYou are now part of our esteemed medical team, dedicated to providing exceptional care to our patients in the {doctor.department} department.\n\nWe look forward to your valuable contributions.\n\nWelcome aboard!\n\nBest regards,\nThe Hospital Management Team'
    sender_email = settings.EMAIL_HOST_USER
    receiver_email = [user_email]
    send_mail(subject, message, sender_email, receiver_email)

    return redirect(reverse('admin-approve-doctor'))

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request,pk):
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)

    # Send rejection email
    user_email = doctor.user.email
    subject = 'Doctor Membership Rejection: Hospital Management System'
    message = f'Hello,\n\nWe regret to inform you that your request to join as a doctor in the {doctor.department} department on our Hospital Management System has been rejected.\n\nIf you have any questions or require further clarification regarding this decision, please feel free to reach out to us.\n\nThank you for your interest.\n\nBest regards,\nThe Hospital Management Team'
    sender_email = settings.EMAIL_HOST_USER
    receiver_email = [user_email]
    send_mail(subject, message, sender_email, receiver_email)

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
    return render(request,'hospital/admin_view_doctor_Specialisation.html', context)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    context = {
        'admin': admin,
        'patients': patients,
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
    
    # Get the last discharge date for the patient
    last_discharge_date = models.PatientDischargeDetails.objects.filter(patientId=patient_id).aggregate(last_discharge=Max('releaseDate'))['last_discharge']
    
    if last_discharge_date:
        try:
            # Get the discharge details corresponding to the last discharge date
            last_discharge = models.PatientDischargeDetails.objects.get(patientId=patient_id, releaseDate=last_discharge_date) 
        except models.PatientDischargeDetails.DoesNotExist:
            last_discharge = None
    else:
        last_discharge = None

    try:
        # Get the insurance object related to the patient
        insurance = models.Insurance.objects.get(patient=patient)
    except models.Insurance.DoesNotExist:
        insurance = None
    
    # Prepare the context dictionary
    context = {
        "admin": admin,
        "patient": patient,
        "insurance": insurance,
        "last_discharge": last_discharge,  
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
            user = userForm.save(commit=False)
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
    patientForm = forms.PatientForm()
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
    else:
        userForm = forms.PatientUserForm()
        patientForm = forms.PatientForm()
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
def approve_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    patient.status = True
    patient.save()

    # Send approval email
    user_email = patient.user.email
    subject = 'Approval Notification: Hospital Management System'
    message = f'Hello,\n\nWe are delighted to inform you that your registration request for our Hospital Management System has been approved.\n\nYou can now access all the features and functionalities available.\n\nThank you for choosing our services!\n\nBest regards,\nThe Hospital Management Team'
    sender_email = settings.EMAIL_HOST_USER
    receiver_email = [user_email]
    send_mail(subject, message, sender_email, receiver_email)

    return redirect(reverse('admin-approve-patient'))

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    user = models.User.objects.get(id=patient.user_id)

    # Send rejection email
    user_email = user.email
    subject = 'Registration Rejection: Hospital Management System'
    message = f'Hello,\n\nWe regret to inform you that your registration request for our Hospital Management System has been rejected.\n\nIf you have any questions or concerns regarding this decision, please don\'t hesitate to contact us.\n\nThank you for considering our services.\n\nBest regards,\nThe Hospital Management Team'
    sender_email = settings.EMAIL_HOST_USER
    receiver_email = [user_email]
    send_mail(subject, message, sender_email, receiver_email)

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
def discharge_patient_view(request, pk):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    patient=models.Patient.objects.get(id=pk)
    days=(date.today()-patient.admit_date)
    assignedDoctor=models.User.objects.all().filter(id=patient.assigned_doctor_id)
    d=days.days
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
        pDD.assignedDoctorName=assignedDoctor[0].get_full_name()
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
        # Pass the ID of the saved object to the template
        patientDict['discharge_id'] = pDD.id

        # Send the bill via email
        subject = 'Your Hospital Bill and Discharge Details'
        message = f'Hello {patient.get_name},\n\nYour hospital bill has been generated. Please find the details below:\n\n' \
          f'Medicine Cost: ${pDD.medicineCost}\n' \
          f'Room Charge: ${pDD.roomCharge}\n' \
          f'Doctor Fee: ${pDD.doctorFee}\n' \
          f'Other Charges: ${pDD.OtherCharge}\n' \
          f'Total: ${patientDict["total"]}\n\n' \
          f'You can view your new invoice and unpaid bills in your discharge panel on the patient portal.\n\n' \
          f'Thank you for choosing our hospital.\n\nBest regards,\nHospital Management Team'
        
        sender_email = settings.EMAIL_HOST_USER
        receiver_email = [patient.user.email]
        send_mail(subject, message, sender_email, receiver_email, fail_silently=False)

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


def download_pdf_view(request, pk, discharge_id):
    try:
        discharge_detail = models.PatientDischargeDetails.objects.get(patientId=pk, id=discharge_id)
    except models.PatientDischargeDetails.DoesNotExist:
        return HttpResponse("Discharge details not found", status=404)

    dict = {
        'patientName': discharge_detail.patientName,
        'assignedDoctorName': discharge_detail.assignedDoctorName,
        'address': discharge_detail.address,
        'mobile': discharge_detail.mobile,
        'symptoms': discharge_detail.symptoms,
        'admitDate': discharge_detail.admitDate,
        'releaseDate': discharge_detail.releaseDate,
        'daySpent': discharge_detail.daySpent,
        'medicineCost': discharge_detail.medicineCost,
        'roomCharge': discharge_detail.roomCharge,
        'doctorFee': discharge_detail.doctorFee,
        'OtherCharge': discharge_detail.OtherCharge,
        'total': discharge_detail.total,
    }
    return render_to_pdf('hospital/download_bill.html', dict)




#-----------------APPOINTMENT START--------------------------------------------------------------------
import datetime
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    appointments = models.Appointment.objects.filter(status__in=[models.Appointment.ACCEPTED, models.Appointment.COMPLETED, models.Appointment.PENDING, models.Appointment.REJECTED])
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    context = {'admin': admin, 'appointments':appointments,   }
    return render(request,'hospital/admin_appointment.html', context)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments = models.Appointment.objects.filter(status__in=[models.Appointment.ACCEPTED, models.Appointment.COMPLETED, models.Appointment.PENDING, models.Appointment.REJECTED])
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
    appointmentForm = forms.AppointmentForm()
    mydict = {'appointmentForm': appointmentForm, 'admin': admin}
    
    if request.method == 'POST':
        appointmentForm = forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment = appointmentForm.save(commit=False)
            appointment.doctorId = request.POST.get('doctorId')
            appointment.patientId = request.POST.get('patientId')
            doctor = models.User.objects.get(id=request.POST.get('doctorId'))
            patient = models.User.objects.get(id=request.POST.get('patientId'))
            appointment.doctorName = doctor.get_full_name()
            appointment.patientName = patient.get_full_name()
            appointment.status = models.Appointment.ACCEPTED
            
            appointment.save()
            
            # Send email notifications to patient and doctor
            current_timezone = timezone.get_current_timezone()
            appointment_date = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%B %d, %Y')
            appointment_time = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%I:%M %p')
            patient_email = patient.email
            doctor_email = doctor.email
            subject = 'Appointment Confirmation'
            patient_message = f'Hello {patient.get_full_name()},\n\nWe are pleased to confirm your appointment with Dr. {appointment.doctorName} on {appointment_date} at {appointment_time}.\n\nPlease remember to arrive at least 15 minutes before your scheduled time.\n\nIf you need to reschedule or have any questions, feel free to contact us.\n\nLooking forward to seeing you!\n\nBest regards,\nThe Hospital Management Team'
            doctor_message = f'Hello Dr. {doctor.get_full_name()},\n\nYou have a new appointment scheduled with {appointment.patientName} on {appointment_date} at {appointment_time}.\n\nPlease ensure you are available at the clinic to attend to the patient.\n\nIf you have any concerns or conflicts with this appointment, kindly inform us as soon as possible.\n\nThank you for your dedication!\n\nBest regards,\nThe Hospital Management Team'
            sender_email = settings.EMAIL_HOST_USER
            patient_receiver_email = [patient_email]
            doctor_receiver_email = [doctor_email]
            send_mail(subject, patient_message, sender_email, patient_receiver_email)
            send_mail(subject, doctor_message, sender_email, doctor_receiver_email)
            
            return HttpResponseRedirect(reverse('admin-view-appointment'))
        else:
            for field, errors in appointmentForm.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    return render(request, 'hospital/admin_add_appointment.html', context=mydict)



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

    # Send email notification to patient
    current_timezone = timezone.get_current_timezone()
    appointment_date = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%B %d, %Y')
    appointment_time = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%I:%M %p')
    patient = models.User.objects.get(id=appointment.patientId)
    doctor = models.User.objects.get(id=appointment.doctorId)
    patient_email = patient.email
    doctor_email = doctor.email
    subject = 'Appointment Confirmation'
    patient_message = f'Hello {patient.get_full_name()},\n\nWe are pleased to confirm your appointment with Dr. {appointment.doctorName} on {appointment_date} at {appointment_time}.\n\nPlease remember to arrive at least 15 minutes before your scheduled time.\n\nIf you need to reschedule or have any questions, feel free to contact us.\n\nLooking forward to seeing you!\n\nBest regards,\nThe Hospital Management Team'
    doctor_message = f'Hello Dr. {doctor.get_full_name()},\n\nYou have a new appointment scheduled with {appointment.patientName} on {appointment_date} at {appointment_time}.\n\nPlease ensure you are available at the clinic to attend to the patient.\n\nIf you have any concerns or conflicts with this appointment, kindly inform us as soon as possible.\n\nThank you for your dedication!\n\nBest regards,\nThe Hospital Management Team'
    sender_email = settings.EMAIL_HOST_USER
    patient_receiver_email = [patient_email]
    doctor_receiver_email = [doctor_email]
    send_mail(subject, patient_message, sender_email, patient_receiver_email)
    send_mail(subject, doctor_message, sender_email, doctor_receiver_email)

    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(appointment_id=pk)
    appointment.status = models.Appointment.REJECTED
    appointment.save()

    # Send email notification to patient
    current_timezone = timezone.get_current_timezone()
    appointment_date = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%B %d, %Y')
    appointment_time = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%I:%M %p')
    patient = models.Patient.objects.get(id=appointment.patientId)
    patient_email = patient.user.email
    subject = 'Appointment Rejection'
    patient_message = f'Hello {patient.user.get_full_name()},\n\nWe regret to inform you that your appointment request with Dr. {appointment.doctorName} on {appointment_date} at {appointment_time} has been rejected.\n\nPlease contact the hospital for further details or to reschedule your appointment.\n\nThank you for your understanding.\n\nBest regards,\nThe Hospital Management Team'
    sender_email = settings.EMAIL_HOST_USER
    receiver_email = [patient_email]
    send_mail(subject, patient_message, sender_email, receiver_email)

    return redirect('admin-approve-appointment')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_set_status_appointment_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    current_datetime = datetime.datetime.now()
    appointments = models.Appointment.objects.filter(status=models.Appointment.ACCEPTED, appointmentDate__lte=current_datetime)
    patient_ids = appointments.values_list('patientId', flat=True)
    patients = models.Patient.objects.filter(status=models.Appointment.ACCEPTED, user_id__in=patient_ids)
    appointments_with_patients = zip(appointments, patients)
    return render(request, 'hospital/admin_status_appointment.html', {'appointments': appointments_with_patients, 'admin': admin})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def set_admin_complete_appointment_view(request,pk):

    appointment = get_object_or_404(models.Appointment, appointment_id=pk)
    patient_id = appointment.patientId
    print(patient_id)
    patient = models.Patient.objects.get(user_id=patient_id)
    
    #Send Email
    current_timezone = timezone.get_current_timezone()
    appointment_date = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%B %d, %Y')
    appointment_time = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%I:%M %p')
    patient_email = patient.user.email
    subject = 'Appointment Completion'
    patient_message = f'Hello {patient.user.get_full_name()},\n\nWe are pleased to inform you that your appointment with Dr. {appointment.doctorName} on {appointment_date} at {appointment_time} has been successfully completed.\n\nWe hope you had a pleasant experience at our hospital and that your health needs were addressed satisfactorily.\n\nThank you for choosing our services!\n\nBest regards,\nThe Hospital Management Team'
    sender_email = settings.EMAIL_HOST_USER
    receiver_email = [patient_email]
    send_mail(subject, patient_message, sender_email, receiver_email)
    
    if appointment.ACCEPTED:
        appointment.status = models.Appointment.COMPLETED
        appointment.save()

        return redirect('admin-status-appointment')
    
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(status=models.Appointment.COMPLETED)
    patientids = appointments.values_list('patientId', flat=True)
    patients = models.Patient.objects.filter(status=True, user_id__in=patientids)
    appointments = zip(appointments, patients)
    
    return render(request, 'hospital/admin_status_appointment.html', {'appointments': appointments, 'admin': admin})

#----------For Handling Billing/Invoice Section
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_billing_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    # Fetch all patients in this model
    patients = models.Patient.objects.all()

    # Initialize a list to store discharge records for patients who have been discharged and paid their bills
    patientDischargeRecords = []

    # Iterate over each patient to check if they have a discharge record
    for patient in patients:
        # Filter discharge records for the current patient already paid his/her bills
        patientRecord = models.PatientDischargeDetails.objects.filter(patientId=patient.id).first()
        if patientRecord:
            # If a discharge record exists for the patient, we add it to the list
            patientDischargeRecords.append(patientRecord)
    context = {
        'admin': admin,
        'patientDischargeRecords': patientDischargeRecords,
    }
    return render(request,'hospital/admin_billing_section.html', context)

#---------Billing Management Section
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_unpaid_bills_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    patients_with_unpaid_bills = models.PatientDischargeDetails.objects.filter(is_Paid=False)
    context = {
        'admin': admin,
        'patients_with_unpaid_bills': patients_with_unpaid_bills,
    }
    return render(request,'hospital/admin_view_unpaid_bills.html', context)


from django.shortcuts import render, get_object_or_404
from . import models

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_invoice(request, patientId, discharge_id):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    
    # Fetch the patient's discharge details and create a copy for the that invoice
    patient= get_object_or_404(models.PatientDischargeDetails, id=discharge_id, patientId=patientId)
    
    
    if patient:
        context = {
            'admin': admin,
            'patient': patient,
            'is_discharged': True,
        }
    else:
        context = {
            'admin': admin,
            'patient': patient,
            'is_discharged': False,
        }    
    return render(request, 'hospital/admin_view_patient_invoice.html', context)

#---- Mark Patient Paid His Bill and deactivate his/her Account
def success_payment_view(request):
    # Implement logic for successful payment
    return render(request, 'hospital/success_payment.html')

def failed_payment_view(request):
    # Implement logic for failed payment
    return render(request, 'hospital/failed_payment.html')

#Enable Webhook for the first time, since Webhooks disabled itself after 12 tries trying to sends a payload to your URL
def enable_webhook():
    webhook = 'hook_Mnxpti1SvGNai4a3bZx6vbr2' #Place your Webhook ID here - you can generate yours at Paymongo Webhooks API
    url = f"https://api.paymongo.com/v1/webhooks/{webhook}/enable"

    headers = {
        "accept": "application/json",
        "authorization": "Basic c2tfdGVzdF9OeGdSOVBTdTlia2JlWDdQWWs1VFR0NUc6cGtfdGVzdF8xU2RIY0hkem55WDJNWW9TeTdlTWpYWlc="
    }

    response = requests.post(url, headers=headers)
    print(f"Status Webhook:{response.text}")

#Function that make the checkout_urls expires within the duration time given
@csrf_exempt
def set_checkout_expiry_date(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        checkout_url = data.get('checkout_url')
        

        if checkout_url:
            # Encode the secret key for Basic Authentication
            auth_header = base64.b64encode(settings.PAYMONGO_SECRET_KEY.encode()).decode()
            
            #Get the Checkout-Session-ID from the Url
            checkout_id = f'cs_{checkout_url.split("cs_")[1].split("_")[0]}' 
            
            print(f'Checkout Session ID expired: {checkout_id}')

            #Expire a Checkout Session API
            url = f"https://api.paymongo.com/v1/checkout_sessions/{checkout_id}/expire"

            headers = {
                "accept": "application/json",
                "authorization": f'Basic {auth_header}'
            }

            expiry_response = requests.post(url, headers=headers) # Send a request via POST method to Paymongo

            # Calculate and return the expiration time
            if expiry_response.ok:
                return JsonResponse({'link': 'Checkout Link Expired', 'status':True})
            else:
                return JsonResponse({'success': False, 'error_message': 'Failed to expire checkout session'}, status=500)
        else:
            return JsonResponse({'success': False, 'error_message': 'Missing checkout_url parameter'}, status=400)            
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'}, status=405)



import base64
@csrf_exempt
def create_payment_session(request):
    if request.method == 'POST':
        try:
            # Retrieve total amount and other charges from the form data
            discharge_id =  request.POST.get('discharge_id')
            roomCharge = int(request.POST.get('roomCharge')) * 100
            medicineCost = int(request.POST.get('medicineCost')) * 100
            doctorFee = int(request.POST.get('doctorFee')) * 100
            otherCharge = int(request.POST.get('OtherCharge')) * 100

            # Encode the secret key for Basic Authentication
            auth_header = base64.b64encode(settings.PAYMONGO_SECRET_KEY.encode()).decode()

            # Construct the request payload
            payload = {
                "data": {
                    "attributes": {
                        "send_email_receipt": False,
                        "show_description": True,
                        "show_line_items": True,
                        "description": "From The Hospital Management Team",
                        "line_items": [
                            {
                                "name": "Room Charge",
                                "quantity": 1,
                                "amount": roomCharge,
                                "currency": "PHP"
                            },
                            {
                                "name": "Medicine Cost",
                                "quantity": 1,
                                "amount": medicineCost,
                                "currency": "PHP"
                            },
                            {
                                "name": "Doctor Fee",
                                "quantity": 1,
                                "amount": doctorFee,
                                "currency": "PHP"
                            },
                            {
                                "name": "Other Charge",
                                "quantity": 1,
                                "amount": otherCharge,
                                "currency": "PHP"
                            },
                        ],
                       "payment_method_types": [
                            "billease",
                            "card",
                            "dob",
                            "dob_ubp",
                            "brankas_bdo",
                            "brankas_landbank",
                            "brankas_metrobank",
                            "gcash",
                            "grab_pay",
                            "paymaya",
                        ],
                        "reference_number": f"{discharge_id}",
                    }
                }
            }

            # Make a POST request to create the payment session
            response = requests.post(
                'https://api.paymongo.com/v1/checkout_sessions',
                json=payload,
                headers={
                    'Authorization': f'Basic {auth_header}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            #Get the Checkout Session Link
            checkout_url = response.json()['data']['attributes']['checkout_url']
            #print(checkout_url)

            # Check if the request was successful
            if response.status_code == 200:
                enable_webhook() #Enable webhook after Creating a session for the first time.
                return JsonResponse({
                    'success': 200,
                    'checkout_url': checkout_url,                   
                })
            else:
                return JsonResponse({'error': 'Failed to create payment session'}, status=response.status_code)

        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error creating payment session: {e}")
            return JsonResponse({'error': 'Failed to create payment session'}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

#Webhook 
@csrf_exempt
def handle_webhook(request):
    if request.method == 'POST':
        # Check if the request body is empty
        if not request.body:
            print("Empty request body")
            return JsonResponse({'error': 'Empty request body'}, status=200)
        else:
            try:
                # Decode the JSON payload
                payload = json.loads(request.body.decode('utf-8'))
                #print(payload) #Print the whole payload JSON
                # Check if the payment status is "paid"
                try:
                    payment_status = payload.get('data', {}).get('attributes', {}).get('data', {}).get('attributes', {}).get('payments', [{}])[0].get('attributes', {}).get('status')
                    reference_number = payload.get('data', {}).get('attributes', {}).get('data', {}).get('attributes', {}).get('reference_number') # Get id as reference_id

                    #print(f"Invoice: {reference_number}")
                    if payment_status == 'paid':
                        mark_patient_bill(reference_number) #Function that sets the bill and mark as paid
                        return JsonResponse({'message': 'Payment successfully processed'}, status=200)
                    
                except KeyError as e:
                    print("KeyError:", e)
                    if str(e) == "'payment_intent'":
                        return JsonResponse({'message': 'Webhook received successfully'}, status=200)
                    else:
                        return JsonResponse({'error': 'KeyError in payment status'}, status=400)
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return JsonResponse({'error': 'Error decoding JSON'}, status=400)
    else:
        # Return an error response for other request methods
        return JsonResponse({'error': 'Invalid request method'}, status=405)

#If payment was successful thru a payment channel
def mark_patient_bill(discharge_id):
    bill = get_object_or_404(models.PatientDischargeDetails, id=discharge_id)
    patient = get_object_or_404(models.Patient, id = bill.patientId)

    # Count the number of bills for the patient
    unpaid_bill_count = models.PatientDischargeDetails.objects.filter(patientId = bill.patientId).count()
   
    if patient:
        #Check if user has less than one bill before deactivating his account
        if unpaid_bill_count <= 1:
            # Get Patient User to set the isActive to False(Deactivate)
            user = patient.user
            user.is_active = False
            user.save() # Save changes

        bill.is_Paid = True #Mark Bill as Paid
        bill.save() # Save Record

        # Send email notification to the patient
        subject = 'Your Hospital Bill Payment Confirmation'
        message = f'Hello {patient.user.get_full_name()},\n\nWe are delighted to inform you that your hospital bill has been successfully paid. Here are the details:\n\nAdmit Date: {bill.admitDate}\nRelease Date: {bill.releaseDate}\nDays Spent: {bill.daySpent}\n\nRoom Charge: ${bill.roomCharge}\nMedicine Cost: ${bill.medicineCost}\nDoctor Fee: ${bill.doctorFee}\nOther Charges: ${bill.OtherCharge}\nTotal Bill: ${bill.total}\n\nThank you for choosing our hospital for your healthcare needs.\n\nBest regards,\nHospital Management Team'
        sender_email = settings.EMAIL_HOST_USER
        receiver_email = [patient.user.email]
        send_mail(subject, message, sender_email, receiver_email)

        return JsonResponse({'success': True}) # Success 

#This is for Receptionist Function when payment happend at the front desk.
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def mark_pay_patient_bill(request, patientId, discharge_id):
    bill = get_object_or_404(models.PatientDischargeDetails, patientId = patientId, id=discharge_id)
    patient = get_object_or_404(models.Patient, id = patientId)

    # Count the number of bills for the patient
    unpaid_bill_count = models.PatientDischargeDetails.objects.filter(patientId=patientId).count()
   
    if bill:
        #Check if user has less than one bill before deactivating his account
        if unpaid_bill_count <= 1:
            # Get Patient User to set the isActive to False(Deactivate)
            user = patient.user
            user.is_active = False
            user.save() # Save changes

        bill.is_Paid = True #Mark Bill as Paid
        bill.save() # Save Record

        # Send email notification to the patient
        subject = 'Your Hospital Bill Payment Confirmation'
        message = f'Hello {patient.user.get_full_name()},\n\nWe are delighted to inform you that your hospital bill has been successfully paid. Here are the details:\n\nAdmit Date: {bill.admitDate}\nRelease Date: {bill.releaseDate}\nDays Spent: {bill.daySpent}\n\nRoom Charge: ${bill.roomCharge}\nMedicine Cost: ${bill.medicineCost}\nDoctor Fee: ${bill.doctorFee}\nOther Charges: ${bill.OtherCharge}\nTotal Bill: ${bill.total}\n\nThank you for choosing our hospital for your healthcare needs.\n\nBest regards,\nHospital Management Team'
        sender_email = settings.EMAIL_HOST_USER
        receiver_email = [patient.user.email]
        send_mail(subject, message, sender_email, receiver_email)

        return JsonResponse({'success': True}) # Success 
    
    return JsonResponse({'success': False})    # Return Reponse to False

#-----Patient Discharge Records Section
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_discharge_records_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    # Fetch all patients in this model
    patients = models.Patient.objects.all()

    # Initialize a list to store discharge records for patients who have been discharged and paid their bills
    patientDischargeRecords = []

    # Iterate over each patient to check if they have a discharge record
    for patient in patients:
        # Filter discharge records for the current patient already paid his/her bills
        patientRecord = models.PatientDischargeDetails.objects.filter(patientId=patient.id).first()
        if patientRecord:
            # If a discharge record exists for the patient, we add it to the list
            patientDischargeRecords.append(patientRecord)

    context = {
        'admin': admin,
        'patientDischargeRecords': patientDischargeRecords,
    }
    return render(request, 'hospital/admin_view_paid_bills.html', context)

#---For Viewing Records History Invoices of that Patient inside of a Ptient Discharge Model
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view_records(request, patientId):
    admin = models.HospitalStaffAdmin.objects.get(user_id=request.user.id)
    # Get all discharge records for the patient
    patient_records = models.PatientDischargeDetails.objects.filter(patientId=patientId)
    
    # Check if any records exist for a given patient
    if patient_records.exists():
        context = {
            'admin': admin,
            'patient_records': patient_records,
        }
    else:
        context = {
            'admin': admin,
            'patient_records': None,  # No records found for the patient
        }
    
    return render(request, 'hospital/admin_patient_view_records.html', context)
    

#----------------Admission Start
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_admission_view(request):
    admin = models.HospitalStaffAdmin.objects.get(user=request.user)
    deactivated_patients = models.Patient.objects.filter(user__is_active=False)
    return render(request, 'hospital/admin_admission.html', {'admin': admin, 'deactivated_patients': deactivated_patients})


#----------------Activate Patient Account During Admission Process.
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reactivate_patient_view(request, pk):
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
            user = userForm.save(commit=False)
            email = request.POST.get('email')
            user.email = email
            user.is_active = True
            # Check if a new password is provided in the form
            new_password = request.POST.get('password')
            if new_password:
                # Set the new password
                user.set_password(new_password)
            user.save()

            patient = patientForm.save(commit=False)
            patient.status = True
            patient.admit_date = date.today()
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
            
            # Sending email notification
            subject = 'Your account has been reactivated!'
            html_message = render_to_string('hospital/reactivate_account_email.html', {'user': user})
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to = [user.email]
            send_mail(subject, plain_message, from_email, to, html_message=html_message)

            return redirect('admin-view-patient')
        else:
            for field, errors in userForm.errors.items():
                for error in errors:
                    messages.error(request, f"User Form: {field.capitalize()} - {error}")
            for field, errors in patientForm.errors.items():
                for error in errors:
                    messages.error(request, f"Patient Form: {field.capitalize()} - {error}")

    mydict = {'userForm': userForm, 'patientForm': patientForm, 'admin': admin,}
    return render(request, 'hospital/admin_reactivate_patient.html', context=mydict)

#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------


#---------------------------------------------------------------------------------
#------------------------ PHARMACIST RELATED VIEWS START -------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_pharmacist)
def pharmacist_dashboard_view(request):
    pharmacist = get_object_or_404(models.Pharmacist, user_id = request.user.id)
    # Count all available medicines that are not out of stock
    medicines_count = models.Medicine.objects.exclude(quantity__lte=0).count()

    # List all medicines that are low on stocks below 10 Quantity
    low_stock_medicines = models.Medicine.objects.filter(quantity__lt=10)

    # Count the number of medicines low on stock for cards
    medicines_low_stock_count = low_stock_medicines.count()

    # Count the total number of manufacturers
    total_manufacturers = models.Manufacturer.objects.count()   

    # Count the number of expired medicines
    expired_medicines_count = models.Medicine.objects.filter(expiry_date__lt=date.today()).count()

    # Count the number of medicines near expiration date (within 30 days)
    near_expiration_medicines_count = models.Medicine.objects.filter(expiry_date__gte=date.today(), expiry_date__lte=date.today() + timedelta(days=30)).count()

    context = {
        'medicines_count': medicines_count,
        'low_stock_medicines': low_stock_medicines,
        'medicines_low_stock_count': medicines_low_stock_count,
        'total_manufacturers': total_manufacturers,
        'expired_medicines_count': expired_medicines_count,
        'near_expiration_medicines_count': near_expiration_medicines_count,
        'pharmacist': pharmacist,
    }

    return render(request, 'hospital/pharmacist_dashboard.html', context)

@login_required(login_url='adminlogin')
@user_passes_test(is_pharmacist)
def pharmacist_medicines_view(request):
    pharmacist = get_object_or_404(models.Pharmacist, user_id = request.user.id)
    # Fetch all medicines
    medicines = models.Medicine.objects.all()

    context = {
        'medicines': medicines,
        'pharmacist': pharmacist,
    }
    return render(request, 'hospital/pharmacist_medicine.html', context)

#Autofill Completion View for Medicines
def autocomplete_view(request):
    search = request.GET.get('query', '')

    # Search for matching medicine names or associated symptoms
    suggestions = models.Medicine.objects.filter(
        Q(name__icontains=search) |
        Q(manufacturer__name__icontains=search) |
        Q(symptoms__name__icontains=search)
    ).select_related('symptoms').values_list('name', 'symptoms__name')

    # Convert suggestions into a list
    suggestions_list = []
    for medicine_name, symptom_name in suggestions:
        if medicine_name not in suggestions_list:
            suggestions_list.append(medicine_name)
        if symptom_name and symptom_name not in suggestions_list:
            suggestions_list.append(symptom_name)

    # Limit the number of suggestions to 10
    suggestions_list = suggestions_list[:10]
    
    return JsonResponse({'suggestions': suggestions_list})

@login_required(login_url='adminlogin')
@user_passes_test(is_pharmacist)
def pharmacist_medicines_list_view(request):
    pharmacist = get_object_or_404(models.Pharmacist, user_id = request.user.id)
    # Fetch all medicines or filter by category if provided
    manufacturers = models.Manufacturer.objects.all()
    medicines = models.Medicine.objects.all().order_by('-id')
    search = request.GET.get('search')
    category = request.GET.get('category')
    manufacturer = request.GET.get('manufacturer')
    
    if category:
        medicines = medicines.filter(category=category)

    if manufacturer:
         # Check if the manufacturer name exists
        if models.Manufacturer.objects.filter(name=manufacturer).exists():
            # If exists, get the manufacturer object
            manufacturer = get_object_or_404(models.Manufacturer, name=manufacturer)
            # Filter medicines by the manufacturer
            medicines = medicines.filter(manufacturer=manufacturer)

    # Search filter
    search = request.GET.get('search')
    if search:
        medicines = medicines.filter(
            Q(name__icontains=search) | 
            Q(manufacturer__name__icontains=search) |
            Q(symptoms__name__icontains=search) #Tag
        )
    
    # Pagination
    items_per_page = 12  
    paginator = Paginator(medicines, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate the total number of pages
    num_pages = paginator.num_pages

    # Define the maximum number of page links to display
    max_page_links = 5

    # Calculate the range of pages to display
    current_page = page_obj.number
    start_page = max(1, current_page - max_page_links // 2)
    end_page = min(num_pages, start_page + max_page_links - 1)

    # Adjust start_page and end_page if not enough pages to display
    if end_page - start_page + 1 < max_page_links:
        start_page = max(1, end_page - max_page_links + 1)

    page_range = range(start_page, end_page + 1)

    context = {
        'manufacturers':manufacturers,
        'medicines': page_obj,
        'page_range': page_range,
        'selected_category': category,
        'selected_manfacturer': manufacturer,
        'pharmacist': pharmacist,
    }
    return render(request, 'hospital/pharmacist_view_medicines.html', context)

@login_required(login_url='adminlogin')
@user_passes_test(is_pharmacist)
def pharmacist_add_medicine(request):
    pharmacist = get_object_or_404(models.Pharmacist, user_id = request.user.id)
    if request.method == 'POST':
        form = forms.MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('pharmacist-medicines')  # Redirect to the pharmacist medicines view after adding medicine
    else:
        form = forms.MedicineForm()
    return render(request, 'hospital/pharmacist_add_medicine.html', {'form': form, 'pharmacist':pharmacist,})

@login_required(login_url='adminlogin')
@user_passes_test(is_pharmacist)
def pharmacist_update_medicine(request, pk):
    pharmacist = get_object_or_404(models.Pharmacist, user_id = request.user.id)
    medicine = get_object_or_404(models.Medicine, pk=pk)
    if request.method == 'POST':
        form = forms.MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            profile_pic = request.FILES.get('profile_pic')  # Assign the uploaded file to the profile_pic field
            medicine = form.save(commit=False)
            if profile_pic:
                medicine.profile_pic = profile_pic
            medicine.save()
            form.save()
            return JsonResponse({'success': True, 'message': 'Medicine updated successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = forms.MedicineForm(instance=medicine)
    return render(request, 'hospital/pharmacist_update_medicine.html', {'form': form, 'pk':pk, 'pharmacist':pharmacist,})

@login_required(login_url='adminlogin')
@user_passes_test(is_pharmacist)
def pharmacist_view_medicine(request, pk):
    pharmacist = get_object_or_404(models.Pharmacist, user_id=request.user.id)  # Current User
    medicine = get_object_or_404(models.Medicine, pk=pk)
    
    # Fetch related medicines from the same manufacturer
    related_medicines = models.Medicine.objects.filter(manufacturer=medicine.manufacturer).exclude(pk=pk)

    # Pagination
    items_per_page = 4  
    paginator = Paginator(related_medicines, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate the total number of pages
    num_pages = paginator.num_pages

    # Define the maximum number of page links to display
    max_page_links = 5

    # Calculate the range of pages to display
    current_page = page_obj.number
    start_page = max(1, current_page - max_page_links // 2)
    end_page = min(num_pages, start_page + max_page_links - 1)

    # Adjust start_page and end_page if not enough pages to display
    if end_page - start_page + 1 < max_page_links:
        start_page = max(1, end_page - max_page_links + 1)

    page_range = range(start_page, end_page + 1)

    context = {
        "pharmacist": pharmacist,
        "medicine": medicine,
        "related_medicines": page_obj,
        'page_range': page_range,
    }

    return render(request, 'hospital/pharmacist_view_medicine.html', context)

#--------Pharmacist Manufacturers
@login_required(login_url='adminlogin')
@user_passes_test(is_pharmacist)
def pharmacist_manufacturers_view(request):
    
    pharmacist = get_object_or_404(models.Pharmacist, user_id = request.user.id)
    manufacturers = models.Manufacturer.objects.all() #Fetch All Manufacturer Objects Instances

    if request.method == 'POST':
        name = request.POST.get('manufacturerName')
        address = request.POST.get('manufacturerAddress')
        contact = request.POST.get('manufacturerContact')

        # Create a new Manufacturer instance
        manufacturer = models.Manufacturer(name=name, address=address, contact_number=contact)
        # Save the Manufacturer instance to the database
        manufacturer.save()
        
        return redirect('pharmacist-manufacturers-view')
    
    context = {
        'pharmacist': pharmacist,
        'manufacturers': manufacturers,
    }

    return render(request, 'hospital/pharmacist_manufacturers.html', context)

@login_required(login_url='adminlogin')
@user_passes_test(is_pharmacist)
def pharmacist_manufacturers_update(request):
    if request.method == 'POST':
        # Assuming you have logic here to retrieve the manufacturer object to update
        manufacturer_id = request.POST.get('manufacturerId')
        manufacturer = get_object_or_404(models.Manufacturer, pk=manufacturer_id)

        # Update the manufacturer object with the new data
        manufacturer.name = request.POST.get('manufacturerName')
        manufacturer.address = request.POST.get('manufacturerAddress')
        manufacturer.contact_number = request.POST.get('manufacturerContact')
        manufacturer.save()

        # Return success response
        return JsonResponse({'message': 'Manufacturer updated successfully.'})

    return HttpResponseBadRequest('Invalid request method.')

@login_required(login_url='adminlogin')
@user_passes_test(is_pharmacist)
def pharmacist_manufacturers_delete(request):
    if request.method == 'POST':
        manufacturer_id = request.POST.get('manufacturerId')
        manufacturer = get_object_or_404(models.Manufacturer, pk=manufacturer_id)
        manufacturer.delete()
        return JsonResponse({'message': 'Manufacturer deleted successfully.'})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

#-------END of Pharmacist Manufacturers

#---------------------------------------------------------------------------------
#------------------------ PHARMACIST RELATED VIEWS START -------------------------
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    #for three cards
    patientcount=models.Patient.objects.all().filter(status=True,assigned_doctor_id=request.user.id).count()
    appointmentcount=models.Appointment.objects.all().filter(status=models.Appointment.ACCEPTED, doctorId=request.user.id).count()
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
    'patients':models.Patient.objects.all().filter(status=True,assigned_doctor_id=request.user.id)
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
    dischargedpatients = models.PatientDischargeDetails.objects.filter(
    assignedDoctorName=request.user.get_full_name()
).distinct()

    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_view_discharge_patient.html',{'dischargedpatients':dischargedpatients,'doctor':doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=models.Appointment.ACCEPTED,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_appointment.html',{'appointments':appointments, 'doctor':doctor })


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

    # Format the appointment date and time
    current_timezone = timezone.get_current_timezone()
    appointment_date = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%B %d, %Y')
    appointment_time = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%I:%M %p')

    # Sending email notification to patient
    patient = models.Patient.objects.get(user_id = appointment.patientId)
    subject = 'Your appointment has been approved!'
    message = f"Dear {patient.user.get_full_name()},\n\nWe're delighted to inform you that your appointment with Dr. {appointment.doctorName} is scheduled for {appointment_date} at {appointment_time}.\n\nPlease arrive at least 15 minutes before the scheduled time.\n\nLooking forward to seeing you!\n\nBest regards,\nDr. {appointment.doctorName}"
    from_email = settings.EMAIL_HOST_USER  # Update with your sender email
    to = [patient.user.email]
    send_mail(subject, message, from_email, to)

    return redirect(reverse('doctor-approve-appointment'))



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def reject_doctor_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(appointment_id=pk)
    appointment.status= models.Appointment.REJECTED
    appointment.save()

    # Sending email notification to patient
    current_timezone = timezone.get_current_timezone()
    appointment_date = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%B %d, %Y')
    appointment_time = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%I:%M %p')
    patient = models.Patient.objects.get(user_id = appointment.patientId)
    subject = 'Your appointment has been rejected'
    message = f"Dear {patient.user.get_full_name()},\n\nWe regret to inform you that your appointment with Dr. {appointment.doctorName} scheduled for {appointment_date} at {appointment_time} has been rejected.\n\nIf you have any questions or concerns, please feel free to contact us.\n\nBest regards,\nDr. {appointment.doctorName}"
    from_email = settings.EMAIL_HOST_USER  # Update with your sender email
    to = [patient.user.email]
    send_mail(subject, message, from_email, to)
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
            appointment.patientName = patient.user.get_full_name()
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

        # Sending email notification to patient
        current_timezone = timezone.get_current_timezone()
        appointment_date = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%B %d, %Y')
        appointment_time = timezone.localtime(appointment.appointmentDate, timezone=current_timezone).strftime('%I:%M %p')
        patient = models.Patient.objects.get(user_id = appointment.patientId)
        subject = 'Your appointment has been completed!'
        message= f'Hello {patient.user.get_full_name()},\n\nWe would like to inform you that your appointment with Dr. {appointment.doctorName} on {appointment_date} at {appointment_time} has been completed.\n\nWe hope you had a pleasant experience at our hospital.\n\nThank you!'
        from_email = settings.EMAIL_HOST_USER  # Update with your sender email
        to = [patient.user.email]
        send_mail(subject, message, from_email, to)

        return redirect('doctor-status-appointment')
        

    doctor = models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments = models.Appointment.objects.filter(status=models.Appointment.COMPLETED, doctorId=request.user.id)
    patientids = appointments.values_list('patientId', flat=True)
    patients = models.Patient.objects.filter(status=True, user_id__in=patientids)
    appointments = zip(appointments, patients)
    
    return render(request, 'hospital/doctor_status_appointment.html', {'appointments': appointments, 'doctor': doctor})

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
    
    appointments = models.Appointment.objects.filter(patientId=request.user.id)
    appointment_date = None
    appointment_status = None
    #Check if there is multiple appointments objects
    if appointments.exists():
        # If there are multiple appointments, take the recent one~!
        appointment = appointments.last()
        appointment_date = appointment.appointmentDate.strftime("%b. %d, %Y %I:%M %p")
        appointment_status = appointment.status

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
    appointments=models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request,'hospital/patient_appointment.html',{'appointments':appointments, 'patient':patient})


from .disease_mappings import disease_to_department #Add More keywords here.
@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    assigned_doctor_id = patient.assigned_doctor_id
    patient_doctors = models.Doctor.objects.filter(status=True, user_id=assigned_doctor_id)
    appointmentForm = forms.PatientAppointmentForm(patient_doctors=patient_doctors)
    message = None

    if request.method == 'POST':
        appointmentForm = forms.PatientAppointmentForm(request.POST, patient_doctors=patient_doctors)
        if appointmentForm.is_valid():
            desc = request.POST.get('description')
            doctor_id = request.POST.get('doctorId')
            doctor = models.Doctor.objects.get(user_id=doctor_id)

            # Check if description contains any disease keyword for doctor's department
            for word in desc.split():
                for disease, department in disease_to_department.items():
                    if word.lower() == disease:
                        if isinstance(department, list):  # Check if multiple departments are associated with the disease
                            if doctor.department in department:
                                break
                        else:
                            if doctor.department == department:
                                break
                else:
                    continue  # Continue to the next word if no match found
                break  # If a match is found, break out of the outer loop

            else:
                messages.error(request, "Please consult your doctor according to the disease.")
                return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})

            appointment = appointmentForm.save(commit=False)
            appointment.doctorId = doctor_id
            appointment.patientId = request.user.id
            appointment.doctorName = f"{doctor.user.first_name} {doctor.user.last_name}"
            appointment.patientName = f"{patient.user.first_name} {patient.user.last_name}"
            appointment.status = models.Appointment.PENDING
            appointment.save()
            
            messages.success(request, 'Appointment booked successfully.')
            return HttpResponseRedirect('patient-view-appointment')
        else:
            for field, errors in appointmentForm.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        appointmentForm = forms.PatientAppointmentForm(patient_doctors=patient_doctors)
    
    return render(request, 'hospital/patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient, 'message': message})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    appointments=models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request,'hospital/patient_view_appointment.html',{'appointments':appointments,'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)  # Fetch patient details
    discharge_details = models.PatientDischargeDetails.objects.filter(patientId=patient.id, is_Paid=False)
    is_discharged = discharge_details.exists()  # Check if any discharge details exist for the patient
    # Encode the secret key for Basic Authentication
    auth_header = base64.b64encode(settings.PAYMONGO_SECRET_KEY.encode()).decode()
    patient_dict = {
        'patient': patient,
        'is_discharged': is_discharged,
        'discharge_details': discharge_details,
        'auth_header': auth_header,
    }
    return render(request, 'hospital/patient_discharge.html', context=patient_dict)

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

