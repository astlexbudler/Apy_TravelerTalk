from django.contrib import admin
from . import models

class ActivityAdmin(admin.ModelAdmin):
  list_display = ['id', 'user_id', 'message', 'created_dt']
  list_filter = ['user_id']
  search_fields = ['message']

admin.site.register(models.ACTIVITY, ActivityAdmin)