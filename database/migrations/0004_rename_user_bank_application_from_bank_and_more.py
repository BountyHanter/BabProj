# Generated by Django 5.1.1 on 2024-10-07 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0003_alter_application_client_bank'),
    ]

    operations = [
        migrations.RenameField(
            model_name='application',
            old_name='user_bank',
            new_name='from_bank',
        ),
        migrations.RenameField(
            model_name='application',
            old_name='client_bank',
            new_name='to_bank',
        ),
    ]
