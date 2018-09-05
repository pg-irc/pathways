from django.contrib import admin
from human_services.phone_numbers import models

admin.site.register(models.PhoneNumberType)
admin.site.register(models.PhoneNumber)
