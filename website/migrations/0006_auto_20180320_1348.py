# Generated by Django 2.0.3 on 2018-03-20 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_person_notes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='actual_fio',
            new_name='fio_actual',
        ),
    ]