from django.contrib import admin
from messaging import models

admin.site.register(models.MessagingGroup)
admin.site.register(models.GroupMessage)
admin.site.register(models.DirectMessage)

