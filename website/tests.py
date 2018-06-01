from django.test import TestCase

from website.models import Person


class PersonTestCase(TestCase):
    def setUp(self):
        Person.objects.create()
        Person.objects.create(fio='a')
        Person.objects.create(fio='b', fio_actual='c')

    def test_unknown_person_name(self):
        person = Person.objects.get(fio='')
        self.assertEqual(person.name(), 'Неизвестный')

    def test_unknown_person_status(self):
        person = Person.objects.get(fio='')
        self.assertEqual(person.get_status(), Person.INCOMPLETE)

    def test_incomplete_person_name(self):
        person = Person.objects.get(fio='a')
        self.assertEqual(person.name(), 'a')

    def test_incomplete_person_status(self):
        person = Person.objects.get(fio='a')
        self.assertEqual(person.get_status(), Person.INCOMPLETE)

    def test_partial_person_name(self):
        person = Person.objects.get(fio='b')
        self.assertEqual(person.name(), 'c')

    def test_partial_person_status(self):
        person = Person.objects.get(fio='b')
        self.assertEqual(person.get_status(), Person.PARTIAL)

    def tearDown(self):
        Person.objects.all().delete()
