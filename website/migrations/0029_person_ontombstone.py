# Generated by Django 2.0.6 on 2018-06-07 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0028_auto_20180607_1749'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='ontombstone',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='На памятнике'),
        ),
    ]