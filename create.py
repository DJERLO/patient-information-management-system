import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospitalmanagement.settings')
django.setup()

from hospital.models import Symptom

def create_symptom(symptom_name):
    # Try to get the Symptom object with the given name
    symptom, created = Symptom.objects.get_or_create(name=symptom_name)
    # If the Symptom object was not created (already exists), print a message
    if not created:
        print(f"Symptom '{symptom_name}' already exists.")
    # If the Symptom object was created, print a message
    else:
        print(f"Symptom '{symptom_name}' created successfully.")

def remove_duplicates(symptom_names):
    existing_symptom_names = set(symptom.name for symptom in Symptom.objects.all())
    for symptom_name in symptom_names:
        if symptom_name in existing_symptom_names:
            symptom_names.remove(symptom_name)
            print(f"Symptom '{symptom_name}' deleted successfully.")

symptom_names = [
    "Pain relief",
    "Fever reduction",
    "Inflammation control",
    "Muscle pain",
    "Joint pain",
    "Arthritis symptoms",
    "Back pain",
    "Neck pain",
    "Headache",
    "Migraine",
    "Menstrual cramps",
    "Menstrual pain",
    "Period pain",
    "Dysmenorrhea",
    "Nasal congestion",
    "Sinus pressure",
    "Runny nose",
    "Sneezing",
    "Cough",
    "Sore throat",
    "Shortness of breath",
    "Wheezing",
    "Chest pain",
    "Heartburn",
    "Acid reflux",
    "Nausea",
    "Vomiting",
    "Diarrhea",
    "Abdominal pain",
    "Constipation",
    "Indigestion",
    "Bloating",
    "Flatulence",
    "Heart palpitations",
    "High blood pressure",
    "Low blood pressure",
    "Irregular heartbeat",
    "Anxiety",
    "Depression",
    "Stress",
    "Insomnia",
    "Fatigue",
    "Weakness",
    "Dizziness",
    "Fainting",
    "Confusion",
    "Memory loss",
    "Blurry vision",
    "Dry eyes",
    "Itchy eyes",
    "Red eyes",
    "Earache",
    "Ear ringing",
    "Ear congestion",
    "Skin rash",
    "Itching",
    "Dry skin",
    "Eczema",
    "Psoriasis",
    "Acne",
    "Burns",
    "Cuts",
    "Bruises",
    "Wounds",
    "Athlete's foot",
    "Fungal infection",
    "Yeast infection",
    "Sexually transmitted infection",
    "Urinary tract infection",
    "Kidney stones",
    "Gastritis",
    "Ulcer",
    "Gallstones",
    "Liver disease",
    "Pancreatitis",
    "Hemorrhoids",
    "Varicose veins",
    "Obesity",
    "Weight loss",
    "Weight gain",
    "Food allergy",
    "Lactose intolerance",
    "Gluten intolerance",
    "Diabetes",
    "Hyperglycemia",
    "Hypoglycemia",
    "Thyroid disorder",
    "Anemia",
    "Vitamin deficiency",
    "Osteoporosis",
    "Arthritis",
    "Osteoarthritis",
    "Rheumatoid arthritis",
    "Gout",
    "Fibromyalgia",
    "Cancer",
    "Allergy",
    "Asthma",
    "Chronic obstructive pulmonary disease (COPD)",
    "Emphysema",
    "Bronchitis",
    "Pneumonia",
    "Tuberculosis",
    "HIV/AIDS",
    "Hepatitis",
    "Influenza",
    "Common cold",
    "Chickenpox",
    "Measles",
    "Mumps",
    "Rubella",
    "Pertussis (whooping cough)",
    "Tetanus",
    "Meningitis",
    "Encephalitis",
    "Polio",
    "Rabies",
    "Yellow fever",
    "Dengue fever",
    "Malaria",
    "Cholera",
    "Typhoid fever",
    "Food poisoning",
    "Heatstroke",
    "Hypothermia",
    "Dehydration",
    "Sunburn",
    "Frostbite",
    "Spider bite",
    "Snake bite",
    "Insect sting",
    "Poisoning",
    "Anaphylaxis",
    "Childhood diseases",
    "Vaccination",
    "Travel health",
    "First aid",
    "Wound care",
    "Medication management",
    "Nutritional supplements",
    "Vitamins",
    "Minerals",
    "Probiotics",
    "Antioxidants",
    "Herbal supplements",
    "Weight management",
    "Dietary restrictions",
    "Healthy eating",
    "Physical activity",
    "Exercise",
    "Fitness",
    "Sports injuries",
    "Rehabilitation",
    "Physical therapy",
    "Occupational therapy",
    "Speech therapy",
    "Alternative medicine",
    "Holistic health",
    "Traditional medicine",
    "Homeopathy",
    "Ayurveda",
    "Chinese medicine",
    "Acupuncture",
    "Chiropractic care",
    "Massage therapy",
    "Aromatherapy",
    "Mental health",
    "Counseling",
    "Therapy",
    "Psychiatry",
    "Substance abuse",
    "Addiction",
    "Recovery",
    "Support groups",
    "Family planning",
    "Birth control",
    "Contraception",
    "Pregnancy",
    "Prenatal care",
    "Childbirth",
    "Postpartum care",
    "Breastfeeding",
    "Infant care",
    "Baby feeding",
    "Childhood nutrition",
    "Pediatric health",
    "Immunization",
    "Childhood illnesses",
    "School health",
    "Adolescent health",
    "Teenage health",
    "Sexual health",
    "Reproductive health",
    "Elderly care",
    "Geriatric health",
    "Aging",
    "Senior nutrition",
    "Dementia",
    "Alzheimer's disease",
    "Parkinson's disease",
    "Mobility aids",
    "Assistive devices",
    "Home health care",
    "Hospice care",
    "Palliative care",
    "End-of-life care",
]

# Make a copy of the symptom_names list
symptom_names_copy = symptom_names.copy()

# Remove any duplicate symptom names from the database
remove_duplicates(symptom_names_copy)

# Loop through each symptom name and create Symptom objects
for symptom_name in symptom_names_copy:
    create_symptom(symptom_name)