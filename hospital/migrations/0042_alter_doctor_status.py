# Generated by Django 5.0.2 on 2024-02-20 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0041_alter_appointment_status_alter_doctor_department_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='status',
            field=models.IntegerField(choices=[(0, 'On Hold'), (1, 'Available'), (2, 'Not Available')], default=0),
        ),
    ]