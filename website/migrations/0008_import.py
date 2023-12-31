# Generated by Django 2.0.3 on 2018-03-22 08:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_auto_20180320_1554'),
    ]

    operations = [
        migrations.CreateModel(
            name='Import',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='import-20180322082241', max_length=255)),
                ('file', models.FileField(upload_to='import/', verbose_name='Файл для импорта')),
                ('cemetery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Cemetery', verbose_name='Захоронение')),
            ],
        ),
    ]
