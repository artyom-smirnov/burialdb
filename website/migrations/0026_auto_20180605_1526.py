# Generated by Django 2.0.6 on 2018-06-05 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0024_remove_hospital_active_import'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='grave',
            field=models.CharField(blank=True, max_length=255, verbose_name='Расположение могилы'),
        ),
        migrations.AlterField(
            model_name='person',
            name='grave_actual',
            field=models.CharField(blank=True, max_length=255, verbose_name='Актуальное расположение могилы'),
        ),
    ]