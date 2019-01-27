# Generated by Django 2.0.6 on 2019-01-27 19:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0039_auto_20190127_1858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='cemetery',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person_cemetery', to='website.Cemetery', verbose_name='Мемориал'),
        ),
        migrations.AlterField(
            model_name='person',
            name='cemetery_actual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person_cemetery_actual', to='website.Cemetery', verbose_name='Актуальный мемориал'),
        ),
    ]
