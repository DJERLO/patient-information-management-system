from typing import Any
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_email, RegexValidator
from hospitalmanagement import settings
from .departments import departments, SPECIALIZATION_CHOICES, MANUFACTURER_CHOICES

class HospitalStaffAdmin(models.Model):
    staff_id = models.AutoField(primary_key=True)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=40, blank=False, null=False)
    profile_pic= models.ImageField(upload_to='profile_pic/StaffAdminProfilePic/',null=True, blank=True)
    address = models.CharField(max_length=40, blank=False, null=False)
    mobile = models.CharField(max_length=20, null=True, blank=False)
    email = models.EmailField(validators=[validate_email], blank=False, null=False)
    status = models.BooleanField(default=False)
    
    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_staff_id(self):
        return self.staff_id

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return f"{self.user.first_name} (StaffAdmin)"
    
class Pharmacist(models.Model):    
    pharmacist_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50)
    address = models.TextField()
    specialization = models.CharField(max_length=100, null=True, blank=True, choices=SPECIALIZATION_CHOICES)
    profile_pic = models.ImageField(blank=True, null=True, upload_to='profile_pic/PharmacistProfilePic/')
    status = models.BooleanField(default=True)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.specialization})"

class Manufacturer(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name
    
class Symptom(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Medicine(models.Model):
    CATEGORY_CHOICES = [
        ('OTC', 'Over-the-counter'),
        ('Prescription', 'Prescription'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=255, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    sold_quantity = models.PositiveIntegerField(default=0)  # Track sold quantity
    expiry_date = models.DateField(blank=True, null=True) # Track expiration date if applicable
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Other')
    profile_pic = models.ImageField(blank=True, null=True, upload_to='medicine/thumbnails/')
    symptoms = models.ManyToManyField(Symptom, related_name='medicines', blank=True)

    def __str__(self):
        return f"{self.name} - {self.dosage} ({self.category})"



class Doctor(models.Model):
    #Status Code
    STATUS_ONHOLD = 0
    STATUS_AVAILABLE = 1
    STATUS_NOTAVAILABLE = 2
    
    STATUS_CHOICES = [
        (STATUS_ONHOLD, 'On Hold'),
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_NOTAVAILABLE, 'Not Available'),
    ]

    user=models.OneToOneField(User,on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=False, null=False)
    mobile_validator = RegexValidator(regex=r'(^(\+)(\d){12}$)|(^\d{11}$)', message= 'Provide a valid Contact Number (e,g: 09172464146 or +639172464146)')
    mobile = models.CharField(max_length=20, validators=[mobile_validator], blank=False, null=False)
    department= models.CharField(max_length=50, choices=departments)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_ONHOLD)
    
    # New field for license number
    license_num_validator = RegexValidator(regex=r'^\d{7}$', message="License number must be 7 digits.")
    license_num = models.CharField(max_length=7, validators=[license_num_validator], unique=True)
    
    profile_pic = models.ImageField(blank=True, null=True, upload_to='profile_pic/DoctorProfilePic/')
   

    def toggle_availability(self):
        if self.status == Doctor.STATUS_AVAILABLE:
            self.status = Doctor.STATUS_NOTAVAILABLE
        elif self.status == Doctor.STATUS_NOTAVAILABLE:
            self.status = Doctor.STATUS_AVAILABLE
        self.save()
   
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    #I fetch three of these and i can set the values on the doctor update form
    @property
    def get_mobile(self):
        return self.mobile
    @property
    def get_address(self):
        return self.address
    @property
    def get_department(self):
        return self.department
    
    @property
    def get_licenseNum(self):
        return self.license_num
    
    @property
    def get_assigned_doctor(self):
        return "{} ({})".format(self.user.first_name,self.department)
        
    def __str__(self):
        return "{} ({})".format(self.user.first_name,self.department)

sex = [('Male','Male'), ('Female','Female'), ('Other','Other')]

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=sex)  # New field
    date_of_birth = models.DateField()
    address = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    status = models.BooleanField(default=False)
    admit_date = models.DateField(auto_now=False)
    profile_pic = models.ImageField(upload_to='profile_pic/PatientProfilePic/', null=True, blank=True)
    
    # Change assigned_doctor_id to reference user_id of hospital_doctor table
    assigned_doctor_id = models.PositiveIntegerField(null=False)
    assigned_doctor = models.CharField(max_length=50)
    symptoms = models.CharField(max_length=100)

    def set_assigned_doctor_id(self, doctor_id):
        self.assigned_doctor_id = doctor_id
    
    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name
    
    @property
    def get_id(self):
        return self.user.id
    
    @property
    def get_admission_date(self):
        return self.admit_date
    
    @property
    def get_gender(self):
        return self.gender
    
    @property
    def get_DOB(self):
        return self.date_of_birth
    
    @property
    def get_address(self):
        return self.address
    
    @property
    def get_mobile(self):
        return self.mobile
    
    @property
    def get_email(self):
        return self.email
    
    @property
    def get_symptoms(self):
        return self.symptoms
    
    @property
    def get_assigned_doctor_id(self):
        return self.assigned_doctor_id
    
    @property
    def get_assigned_doctor(self):
        return self.assigned_doctor

    def __str__(self):
        return self.user.first_name + " (" + self.symptoms + ")"


class Appointment(models.Model):
    #Status Code
    PENDING = 0
    ACCEPTED = 1
    COMPLETED = 2
    REJECTED = 3

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (COMPLETED, 'Completed'),
        (REJECTED, 'Rejected'),
    ]

    appointment_id = models.AutoField(primary_key=True)
    patientId=models.PositiveIntegerField(null=True)
    doctorId=models.PositiveIntegerField(null=True)
    patientName=models.CharField(max_length=40,null=True)
    doctorName=models.CharField(max_length=40,null=True)
    appointmentDate=models.DateTimeField()
    description=models.TextField(max_length=500)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f'Appointment From {self.doctorName}'
    
    
class Insurance(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, null=True, blank=True)
    insurance_provider = models.CharField(max_length=100, blank=True)
    policy_number = models.CharField(max_length=100, blank=True)
    group_number = models.CharField(max_length=100, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    copayment_info = models.CharField(max_length=100, blank=True)
    status = models.BooleanField(default=True)  # True for active, False for expired

    def save(self, *args, **kwargs):
        # Calculate today's date
        today = timezone.now().date()

        # Check if the expiration date is before today's date
        if self.expiration_date and self.expiration_date < today:
            self.status = False  # Set status to False (expired)
        else:
            self.status = True  # Set status to True (active)

        # Call the original save() method
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Insurance for {self.patient}"


class PatientDischargeDetails(models.Model):
    patientId=models.PositiveIntegerField(null=True)
    patientName=models.CharField(max_length=40)
    assignedDoctorName=models.CharField(max_length=40)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=True)
    symptoms = models.CharField(max_length=100,null=True)

    admitDate=models.DateField(null=False)
    releaseDate=models.DateField(null=False)
    daySpent=models.PositiveIntegerField(null=False)

    roomCharge=models.PositiveIntegerField(null=False)
    medicineCost=models.PositiveIntegerField(null=False)
    doctorFee=models.PositiveIntegerField(null=False)
    OtherCharge=models.PositiveIntegerField(null=False)
    total=models.PositiveIntegerField(null=False)
    is_Paid= models.BooleanField(default=False)

    @classmethod
    def check_unpaid_invoices_and_send_email(cls):
        last_email_sent_time = timezone.now() - timedelta(hours=24)  # Example: 24 hours ago
        if last_email_sent_time < timezone.now() - timedelta(hours=24):
            unpaid_invoices = cls.objects.filter(is_Paid=False)
            for invoice in unpaid_invoices:
                # Send email notification
                subject = 'Unpaid Hospital Bill Notification'
                message = f'Hello {invoice.patientName},\n\nWe hope this message finds you well.\n\nWe\'d like to remind you that there is an outstanding balance on your hospital bill. To view and settle your invoice, you can log in to your patient portal and access it under the Discharge panel in the side navigation menu.\n\nPlease ensure the payment is settled at your earliest convenience. If you have any questions or need assistance, feel free to reach out to our support team.\n\nThank you for your prompt attention to this matter.\n\nBest regards,\nThe Hospital Management Team'
                send_mail(subject, message, settings.EMAIL_HOST_USER, [invoice.user.email])
