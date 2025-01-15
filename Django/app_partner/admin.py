from django.contrib import admin
from . import models

class CategoryAdmin(admin.ModelAdmin):
  list_display = ['id', 'parent_id', 'name']
  list_filter = ['parent_id']
  search_fields = ['name']

admin.site.register(models.CATEGORY, CategoryAdmin)