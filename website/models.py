from django.db import models
from django.urls import reverse


class Cemetery(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Hospital(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Person(models.Model):
    cemetery = models.ForeignKey(Cemetery, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_cemetery', verbose_name='Захоронение')
    cemetery_actual = models.ForeignKey(Cemetery, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_cemetery_actual', verbose_name='Актуальное захоронение')

    hospital = models.ForeignKey(Hospital, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_hospital', verbose_name='Госпиталь')
    hospital_actual = models.ForeignKey(Hospital, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_hospital_actual', verbose_name='Актуальный госпиталь')

    fio = models.CharField(max_length=255, blank=True, verbose_name='ФИО')
    fio_actual = models.CharField(max_length=255, blank=True, verbose_name='Актуальные ФИО')

    notes = models.TextField(blank=True, verbose_name='Примечания')

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