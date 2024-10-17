# Generated by Django 5.1.1 on 2024-10-16 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0016_alter_report_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='problems_chat_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='ID чата для проблем с оплатой'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='receipt_chat_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='ID чата для чеков'),
        ),
    ]
