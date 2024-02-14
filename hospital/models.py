from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_email

class HospitalStaffAdmin(models.Model):
    staff_id = models.AutoField(primary_key=True)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=40, blank=False, null=False)
    profile_pic= models.ImageField(upload_to='profile_pic/StaffAdminProfilePic/',null=True, blank=True)
    address = models.CharField(max_length=40, blank=False, null=False)
    mobile = models.CharField(max_length=20, null=True, blank=False)
    email = models.EmailField(validators=[validate_email], blank=False, null=False)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return f"{self.user.first_name} (StaffAdmin)"

departments=[('Cardiologist', 'Cardiologist'),
    ('Dermatologists', 'Dermatologists'),
    ('Emergency Medicine Specialists', 'Emergency Medicine Specialists'),
    ('Allergists/Immunologists', 'Allergists/Immunologists'),
    ('Anesthesiologists', 'Anesthesiologists'),
    ('Colon and Rectal Surgeons', 'Colon and Rectal Surgeons'),
    ('Gastroenterologists', 'Gastroenterologists'),
    ('Hematologists', 'Hematologists'),
    ('Nephrologists', 'Nephrologists'),
    ('Neurologists', 'Neurologists'),
    ('Oncologists', 'Oncologists'),
    ('Ophthalmologists', 'Ophthalmologists'),
    ('Orthopedic Surgeons', 'Orthopedic Surgeons'),
    ('Pediatricians', 'Pediatricians'),
    ('Psychiatrists', 'Psychiatrists'),
    ('Radiologists', 'Radiologists'),
    ('Rheumatologists', 'Rheumatologists')
]
class Doctor(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/DoctorProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=255, blank=False, null=False)
    mobile = models.CharField(max_length=20,blank=False, null=False)
    department= models.CharField(max_length=50, choices=departments,default='Cardiologist')
    status=models.BooleanField(default=False)
   
   
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
    def get_assigned_doctor(self):
        return "{} ({})".format(self.user.first_name,self.department)
        
    def __str__(self):
        return "{} ({})".format(self.user.first_name,self.department)

sex = [('Unspecify', 'Unspecify'),('Male','Male'), ('Female','Female')]

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=sex, default="Choose your Sex")  # New field
    date_of_birth = models.DateField()
    address = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    status = models.BooleanField(default=False)
    admit_date = models.DateField(auto_now=True)
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
    PENDING = 0
    ACCEPTED = 1
    REJECTED = 2

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]
    
    patientId=models.PositiveIntegerField(null=True)
    doctorId=models.PositiveIntegerField(null=True)
    patientName=models.CharField(max_length=40,null=True)
    doctorName=models.CharField(max_length=40,null=True)
    appointmentDate=models.DateTimeField()
    description=models.TextField(max_length=500)
    status=models.BooleanField(default=False)

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


#Developed By : sumit kumar
#facebook : fb.com/sumit.luv
#Youtube :youtube.com/lazycoders
