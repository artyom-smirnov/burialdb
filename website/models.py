import datetime
import os

from django.db import models
from django.db.models import Case, When, CharField
from django.db.models.functions import Coalesce
from django.urls import reverse


class Cemetery(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('cemetery_detail', kwargs={'pk': self.pk})


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

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('import_view', kwargs={'pk': self.pk})

    def delete(self, *args, **kwargs):
        os.unlink(self.file.path)
        super(Import, self).delete(*args, **kwargs)


class Hospital(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('hospital_detail', kwargs={'pk': self.pk})


class PersonManager(models.Manager):
    def get_queryset(self):
        q = super(PersonManager, self).get_queryset()

        q = q.annotate(
            screen_name=Coalesce(
                Case(
                    When(fio_actual__exact='', then=None),
                    When(fio_actual__isnull=False, then='fio_actual'),
                    default=None,
                    output_field=CharField()
                ),
                Case(
                    When(fio__exact='', then=None),
                    When(fio__isnull=False, then='fio'),
                    default=None,
                    output_field=CharField()
                ),
                Case(
                    When(ontombstone__exact='', then=None),
                    When(ontombstone__isnull=False, then='ontombstone'),
                    default=None,
                    output_field=CharField()
                )
            ),
            screen_born_region=Coalesce(
                Case(
                    When(born_region_actual__exact='', then=None),
                    When(born_region_actual__isnull=False, then='born_region_actual'),
                    default=None,
                    output_field=CharField()
                ),
                Case(
                    When(born_region__exact='', then=None),
                    When(born_region__isnull=False, then='born_region'),
                    default=None,
                    output_field=CharField()
                )
            ),
            screen_born_address=Coalesce(
                Case(
                    When(born_address_actual__exact='', then=None),
                    When(born_address_actual__isnull=False, then='born_address_actual'),
                    default=None,
                    output_field=CharField()
                ),
                Case(
                    When(born_address__exact='', then=None),
                    When(born_address__isnull=False, then='born_address'),
                    default=None,
                    output_field=CharField()
                )
            ),
            screen_address=Coalesce(
                Case(
                    When(address_actual__exact='', then=None),
                    When(address_actual__isnull=False, then='address_actual'),
                    default=None,
                    output_field=CharField()
                ),
                Case(
                    When(address__exact='', then=None),
                    When(address__isnull=False, then='address'),
                    default=None,
                    output_field=CharField()
                )
            ),
            screen_military_unit=Coalesce(
                Case(
                    When(military_unit_actual__exact='', then=None),
                    When(military_unit_actual__isnull=False, then='military_unit_actual'),
                    default=None,
                    output_field=CharField()
                ),
                Case(
                    When(military_unit__exact='', then=None),
                    When(military_unit__isnull=False, then='military_unit'),
                    default=None,
                    output_field=CharField()
                )
            ),
        )

        return q


class Person(models.Model):
    INCOMPLETE = 0
    PARTIAL = 1
    COMPLETE = 2

    TREATED = 0
    MIA = 1
    KILLED = 2
    DEADINROAD = 3
    DEADINCAPTIVITY = 4

    STATES = (
        (TREATED, 'Лечился'),
        (MIA, 'Пропал без вести'),
        (KILLED, 'Убит'),
        (DEADINROAD, 'Умер по пути в госпиталь'),
        (DEADINCAPTIVITY, 'Погиб в плену'),
    )

    active_import = models.ForeignKey(Import, null=True, blank=True, on_delete=models.SET_NULL)

    ontombstone = models.CharField(max_length=1024, blank=True, null=True, verbose_name='На памятнике')

    state = models.IntegerField(choices=STATES, default=TREATED, verbose_name='Категория')

    cemetery = models.ForeignKey(Cemetery, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_cemetery', verbose_name='Кладбище')
    cemetery_actual = models.ForeignKey(Cemetery, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_cemetery_actual', verbose_name='Актуальное кладбище')

    hospital = models.CharField(max_length=255, blank=True, null=True, verbose_name='Госпиталь')
    hospital_actual = models.ForeignKey(Hospital, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_hospital_actual', verbose_name='Актуальный госпиталь')

    fio = models.CharField(max_length=255, blank=True, null=True, verbose_name='ФИО (список, прочие источники)')
    fio_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальные ФИО (список, прочие источники)')

    year = models.CharField(max_length=255, null=True, blank=True, verbose_name='Год рождения')
    year_actual = models.IntegerField(null=True, blank=True, verbose_name='Актуальный год рождения')

    born_region = models.CharField(max_length=255, blank=True, null=True, verbose_name='Регион (страна) рождения')
    born_region_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальный регион (страна) рождения')

    born_address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Адрес рождения')
    born_address_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальный адрес рождения')

    conscription_place = models.CharField(max_length=255, blank=True, null=True, verbose_name='Место призыва')
    conscription_place_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальное место призыва')

    military_unit = models.CharField(max_length=255, blank=True, null=True, verbose_name='Часть')
    military_unit_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальная часть')

    rank = models.CharField(max_length=255, blank=True, null=True, verbose_name='Звание')
    rank_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальное звание')

    position = models.CharField(max_length=255, blank=True, null=True, verbose_name='Должность')
    position_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальная должность')

    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Место жительства')
    address_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальное место жительства')

    relatives = models.CharField(max_length=1024, blank=True, null=True, verbose_name='Родственники')
    relatives_actual = models.CharField(max_length=1024, blank=True, null=True, verbose_name='Актуальные родственники')

    receipt_date = models.CharField(max_length=255, blank=True, null=True, verbose_name='Дата поступления')
    receipt_date_actual = models.DateTimeField(null=True, blank=True, verbose_name='Актуальная дата поступления')

    receipt_cause = models.TextField(blank=True, null=True, verbose_name='Причина поступления')
    receipt_cause_actual = models.TextField(blank=True, null=True, verbose_name='Актуальная причина поступления')

    death_date = models.CharField(max_length=255, blank=True, null=True, verbose_name='Дата смерти')
    death_date_actual = models.DateTimeField(null=True, blank=True, verbose_name='Актуальная дата смерти')

    death_cause = models.TextField(blank=True, null=True, verbose_name='Причина смерти')
    death_cause_actual = models.TextField(blank=True, null=True, verbose_name='Актуальная причина смерти')

    grave = models.CharField(max_length=255, blank=True, null=True, verbose_name='Расположение могилы')
    grave_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальное расположение могилы')

    date_of_captivity = models.CharField(max_length=255, blank=True, null=True, verbose_name='Дата пленения')
    date_of_captivity_actual = models.DateTimeField(null=True, blank=True, verbose_name='Актуальная дата пленения')

    place_of_captivity = models.CharField(max_length=255, blank=True, null=True, verbose_name='Место пленения')
    place_of_captivity_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальное место пленения')

    camp = models.CharField(max_length=255, blank=True, null=True, verbose_name='Лагерь')
    camp_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальный лагерь')

    camp_number = models.CharField(max_length=255, null=True, blank=True, verbose_name='Лагерный номер')
    camp_number_actual = models.IntegerField(null=True, blank=True, verbose_name='Актуальный лагерный номер')

    lost_date = models.CharField(max_length=255, blank=True, null=True, verbose_name='Связь прекращена')
    lost_date_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальная дата прекращения связи')

    field_post = models.CharField(max_length=255, blank=True, null=True, verbose_name='Полевая почта')
    field_post_actual = models.CharField(max_length=255, blank=True, null=True, verbose_name='Актуальная полевая почта')

    notes = models.TextField(blank=True, verbose_name='Примечания')

    _single_mapped_fields = [
        'ontombstone',
        'state',
    ]

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
        'grave',
        'date_of_captivity',
        'place_of_captivity',
        'camp',
        'camp_number',
        'lost_date',
        'field_post'
    ]

    _hide_if_treated = [
        'date_of_captivity',
        'place_of_captivity',
        'camp',
        'camp_number',
        'lost_date',
        'field_post'
    ]

    _hide_if_mia = [
        'hospital',
        'receipt_date',
        'receipt_cause',
        'death_date',
        'death_cause',
        'grave',
        'date_of_captivity',
        'place_of_captivity',
        'camp',
        'camp_number'
    ]

    _hide_if_killed = [
        'hospital',
        'receipt_date',
        'receipt_cause',
        'death_cause',
        'date_of_captivity',
        'place_of_captivity',
        'camp',
        'camp_number',
        'lost_date',
        'field_post'
    ]

    _hide_if_dead_in_road = [
        'date_of_captivity',
        'place_of_captivity',
        'camp',
        'camp_number',
        'lost_date',
        'field_post'
    ]

    _hide_if_dead_in_captivity = [
        'hospital',
        'receipt_date',
        'receipt_cause',
        'death_cause',
        'lost_date',
        'field_post'
    ]

    _pair_card_fields = ['cemetery'] + _mapped_fields
    _other_card_fields = ['notes']

    _search_mapping = {
        'fio': ['fio', 'fio_actual', 'ontombstone'],
        'born_year': ['year', 'year_actual'],
        'state': ['state']
    }

    _search_filters_mapping = {
        'fio': '__icontains',
        'born_year': '__contains',
        'state': ''}

    objects = PersonManager()

    def __str__(self):
        return self.name()

    def name(self):
        if self.fio_actual:
            return self.fio_actual
        elif self.fio:
            return self.fio
        elif self.ontombstone:
            return self.ontombstone
        else:
            return 'Неизвестный'

    def living_place(self):
        l = list(filter(lambda item: item, [self.screen_born_region, self.screen_born_address, self.screen_address]))
        return ', '.join(l)

    # TODO: Rework with COALESCE
    def screen_year(self):
        if self.year_actual:
            return self.year_actual
        elif self.year:
            return self.year
        return None

    # TODO: Rework with COALESCE
    def screen_death_date(self):
        if self.death_date_actual:
            return self.death_date_actual
        elif self.death_date:
            return self.death_date
        return None

    # TODO: Rework with COALESCE
    def screen_cemetery(self):
        if self.cemetery_actual:
            return self.cemetery_actual
        elif self.cemetery:
            return self.cemetery
        return None

    def get_absolute_url(self):
        return reverse('person_detail', kwargs={'pk': self.pk})

    @classmethod
    def get_mapped_fields(cls):
        return cls._single_mapped_fields + cls._mapped_fields

    @classmethod
    def get_pair_card_fields(cls):
        return [(x, x + '_actual') for x in cls._pair_card_fields]

    @classmethod
    def get_other_card_fields(cls):
        return cls._other_card_fields

    @classmethod
    def translate_mapped_field_value(cls, field_name, value, active_import=None):
        return value

    @classmethod
    def get_search_mapping(cls):
        return cls._search_mapping

    def get_status(self):
        skipped_some = False
        have_some = False
        for f, f_actual in self.get_pair_card_fields():
            if self.__getattribute__(f_actual):
                have_some = True
            else:
                skipped_some = True
            if have_some and skipped_some:
                return self.PARTIAL

        if have_some and not skipped_some:
            return self.COMPLETE
        elif have_some and skipped_some:
            return self.PARTIAL
        else:
            return self.INCOMPLETE

    def save(self, *args, **kwargs):
        if self.ontombstone:
            self.ontombstone = self.ontombstone.title()
        if self.fio:
            self.fio = self.fio.title()
        if self.fio_actual:
            self.fio_actual = self.fio_actual.title()
        super(Person, self).save(*args, **kwargs)
