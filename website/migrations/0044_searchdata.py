# Generated by Django 2.0.6 on 2020-01-10 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0043_unaccent_extension'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.BinaryField(db_index=True, max_length=20)),
                ('fields', models.TextField()),
            ],
        ),
    ]
