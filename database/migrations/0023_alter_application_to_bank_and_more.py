# Generated by Django 5.1.1 on 2024-11-14 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0022_userprofile_recipients_bank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='to_bank',
            field=models.CharField(verbose_name='Банк получателя средств'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='recipients_bank',
            field=models.JSONField(blank=True, null=True, verbose_name='Банки для перевода'),
        ),
    ]
