# Generated by Django 5.0.1 on 2024-02-02 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0022_alter_hospitalstaffadmin_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='hospitalstaffadmin',
            name='username',
            field=models.CharField(default=1, max_length=40),
            preserve_default=False,
        ),
    ]