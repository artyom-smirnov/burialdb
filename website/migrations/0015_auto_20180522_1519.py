# Generated by Django 2.0.5 on 2018-05-22 15:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0014_auto_20180517_1225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='import',
            name='cemetery',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='website.Cemetery', verbose_name='Захоронение'),
        ),
    ]
