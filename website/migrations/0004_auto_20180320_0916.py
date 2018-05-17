# Generated by Django 2.0.3 on 2018-03-20 09:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_auto_20180319_1402'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cemetery',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='hospital',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['fio']},
        ),
        migrations.AddField(
            model_name='person',
            name='cemetery_actual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person_cemetery_actual', to='website.Cemetery'),
        ),
        migrations.AddField(
            model_name='person',
            name='hospital_actual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person_hospital_actual', to='website.Hospital'),
        ),
        migrations.AlterField(
            model_name='person',
            name='cemetery',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person_cemetery', to='website.Cemetery'),
        ),
        migrations.AlterField(
            model_name='person',
            name='fio',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='hospital',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person_hospital', to='website.Hospital'),
        ),
    ]