import datetime

from django.db import models
from django.urls import reverse


class Cemetery(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


def default_import_name():
    return 'import-%s' % datetime.datetime.now().strftime("%Y%m%d%H%M%S")


class Import(models.Model):
    name = models.CharField(max_length=255, default=default_import_name)
    cemetery = models.ForeignKey(Cemetery, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Захоронение')
    file = models.FileField(upload_to='import/', verbose_name='Файл для импорта')
    header = models.IntegerField(default=1, verbose_name='Строки заголовка')
    numbering = models.IntegerField(default=1, verbose_name='Колонки нумерации')
    delimiter = models.CharField(max_length=1, default=',', verbose_name='Разделитель')
    quotechar = models.CharField(max_length=1, default='"', verbose_name='Символ строки')
    data_added = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('import_update', kwargs={'pk': self.pk})


class Hospital(models.Model):
    name = models.CharField(max_length=255)
    active_import = models.ForeignKey(Import, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Person(models.Model):
    active_import = models.ForeignKey(Import, null=True, blank=True, on_delete=models.SET_NULL)

    cemetery = models.ForeignKey(Cemetery, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_cemetery', verbose_name='Кладбище')
    cemetery_actual = models.ForeignKey(Cemetery, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_cemetery_actual', verbose_name='Актуальное кладбище')

    hospital = models.ForeignKey(Hospital, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_hospital', verbose_name='Госпиталь')
    hospital_actual = models.ForeignKey(Hospital, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_hospital_actual', verbose_name='Актуальный госпиталь')

    fio = models.CharField(max_length=255, blank=True, verbose_name='ФИО')
    fio_actual = models.CharField(max_length=255, blank=True, verbose_name='Актуальные ФИО')

    year = models.CharField(max_length=50, null=True, blank=True, verbose_name='Год рождения')
    year_actual = models.IntegerField(null=True, blank=True, verbose_name='Актуальный год рождения')

    born_region = models.CharField(max_length=255, blank=True, verbose_name='Регион (страна) рождения')
    born_region_actual = models.CharField(max_length=255, blank=True, verbose_name='Актуальный регион (страна) рождения')

    born_address = models.CharField(max_length=255, blank=True, verbose_name='Адрес рождения')
    born_address_actual = models.CharField(max_length=255, blank=True, verbose_name='Актуальный адрес рождения')

    conscription_place = models.CharField(max_length=255, blank=True, verbose_name='Место призыва')
    conscription_place_actual = models.CharField(max_length=255, blank=True, verbose_name='Актуальное место призыва')

    military_unit = models.CharField(max_length=50, blank=True, verbose_name='Часть')
    military_unit_actual = models.CharField(max_length=50, blank=True, verbose_name='Актуальная часть')

    rank = models.CharField(max_length=50, blank=True, verbose_name='Звание')
    rank_actual = models.CharField(max_length=50, blank=True, verbose_name='Актуальное звание')

    position = models.CharField(max_length=50, blank=True, verbose_name='Должность')
    position_actual = models.CharField(max_length=50, blank=True, verbose_name='Актуальная должность')

    address = models.CharField(max_length=255, blank=True, verbose_name='Место жительства')
    address_actual = models.CharField(max_length=255, blank=True, verbose_name='Актуальное место жительства')

    relatives = models.CharField(max_length=1024, blank=True, verbose_name='Родственники')
    relatives_actual = models.CharField(max_length=1024, blank=True, verbose_name='Актуальные родственники')

    receipt_date = models.CharField(max_length=50, blank=True, verbose_name='Дата поступления')
    receipt_date_actual = models.DateTimeField(null=True, blank=True, verbose_name='Актуальная дата поступления')

    receipt_cause = models.CharField(max_length=255, blank=True, verbose_name='Причина поступления')
    receipt_cause_actual = models.CharField(max_length=255, blank=True, verbose_name='Актуальная причина поступления')

    death_date = models.CharField(max_length=255, blank=True, verbose_name='Дата смерти')
    death_date_actual = models.DateTimeField(null=True, blank=True, verbose_name='Актуальная дата смерти')

    death_cause = models.CharField(max_length=255, blank=True, verbose_name='Причина смерти')
    death_cause_actual = models.CharField(max_length=255, blank=True, verbose_name='Актуальная причина смерти')

    grave = models.CharField(max_length=50, blank=True, verbose_name='Номер могилы')
    grave_actual = models.IntegerField(null=True, blank=True, verbose_name='Актуальный номер могилы')

    notes = models.TextField(blank=True, verbose_name='Примечания')

    _mapped_fields = [
        'fio',
        'year',
        'born_region',
        'born_address',
        'conscription_place',
        'military_unit',
        'rank',
        'position',
        'address',
        'relatives',
        'hospital',
        'receipt_date',
        'receipt_cause',
        'death_date',
        'death_cause',
        'grave'
    ]

    _pair_card_fields = _mapped_fields + ['cemetery']
    _other_card_fields = ['notes']

    class Meta:
        ordering = ["fio"]

    def __str__(self):
        return self.name()

    def name(self):
        if self.fio_actual:
            return self.fio_actual
        elif self.fio:
            return self.fio
        else:
            return 'Неизвестный'

    def get_absolute_url(self):
        return reverse('person_detail', kwargs={'pk': self.pk})

    @classmethod
    def get_mapped_fields(cls):
        return cls._mapped_fields

    @classmethod
    def get_pair_card_fields(cls):
        return [(x, x + '_actual') for x in cls._pair_card_fields]

    @classmethod
    def get_other_card_fields(cls):
        return cls._other_card_fields

    @classmethod
    def translate_mapped_field_value(cls, field_name, value, active_import=None):
        if field_name == 'hospital':
            value = value.strip()
            if value:
                hospital, created = Hospital.objects.get_or_create(name=value)
                if active_import and created:
                    hospital.active_import = active_import
                    hospital.save()
                return hospital
            else:
                return None
        else:
            return value

