# Generated by Django 5.1.2 on 2025-07-19 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tourapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyprofile',
            name='bank',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='companyprofile',
            name='bank_account_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
