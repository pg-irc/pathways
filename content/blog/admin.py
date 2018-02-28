from django.contrib import admin
from content.blog import models

admin.site.register(models.BlogIndexPage)
admin.site.register(models.BlogPage)
