# Generated by Django 2.0.5 on 2018-05-22 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_auto_20180522_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='import',
            name='cemetery',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.Cemetery', verbose_name='Захоронение'),
        ),
    ]
