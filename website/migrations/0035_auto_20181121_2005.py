# Generated by Django 2.0.6 on 2018-11-21 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0034_remove_person_mia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='state',
            field=models.IntegerField(choices=[(0, 'Лечился'), (1, 'Пропал без вести'), (2, 'Убит'), (3, 'Умер по пути в госпиталь')], default=0, verbose_name='Категория'),
        ),
    ]