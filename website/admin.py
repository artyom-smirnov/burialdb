from django.contrib import admin

from website.models import Person, Cemetery, Hospital

admin.site.register(Person)
admin.site.register(Cemetery)
admin.site.register(Hospital)
