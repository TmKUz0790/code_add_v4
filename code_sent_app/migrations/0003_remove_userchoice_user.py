# Generated by Django 5.1 on 2024-09-04 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('code_sent_app', '0002_remove_userchoice_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userchoice',
            name='user',
        ),
    ]
