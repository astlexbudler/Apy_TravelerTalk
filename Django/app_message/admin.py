from django.contrib import admin
from . import models

class MessageAdmin(admin.ModelAdmin):
  list_display = ['id', 'sender_id', 'receiver_id', 'title', 'send_dt', 'read_dt']
  list_filter = ['sender_id', 'receiver_id']
  search_fields = ['title']

admin.site.register(models.MESSAGE, MessageAdmin)