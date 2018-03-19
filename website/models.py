from django.db import models


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
    cemetery = models.ForeignKey(Cemetery, null=True, blank=True, on_delete=models.SET_NULL)
    hospital = models.ForeignKey(Hospital, null=True, blank=True, on_delete=models.SET_NULL)

    fio = models.CharField(max_length=255, blank=True)
    actual_fio = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["fio"]

    def __str__(self):
        return self.name()

    def name(self):
        if self.actual_fio:
            return self.actual_fio
        elif self.fio:
            return self.fio
        else:
            return 'Неизвестный'
