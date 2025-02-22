# Generated by Django 5.1.1 on 2024-10-10 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0013_application_closing_rate_application_percentage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='closing_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Курс на момент исполнения заявки'),
        ),
        migrations.AlterField(
            model_name='application',
            name='rate_after_fee',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Курс за вычетом комиссии'),
        ),
    ]
