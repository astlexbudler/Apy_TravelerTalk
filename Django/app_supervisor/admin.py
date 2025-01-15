from django.contrib import admin
from . import models

class BannerAdmin(admin.ModelAdmin):
  list_display = ['id', 'location', 'link']
  list_filter = ['location']
  search_fields = ['link']

admin.site.register(models.BANNER, BannerAdmin)