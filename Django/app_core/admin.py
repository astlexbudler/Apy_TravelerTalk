from django.contrib import admin
from . import models

class CustomUserAdmin(admin.ModelAdmin):
  list_display = ['id', 'username', 'first_name', 'last_login', 'account_type', 'status']
  list_filter = ['account_type', 'status']
  search_fields = ['username', 'first_name']

class UploadAdmin(admin.ModelAdmin):
  list_display = ['file']
  list_filter = ['file']
  search_fields = ['file']

class ServerSettingAdmin(admin.ModelAdmin):
  list_display = ['id', 'value']
  list_filter = ['id']
  search_fields = ['id']

class LevelRuleAdmin(admin.ModelAdmin):
  list_display = ['level', 'required_point', 'name', 'text_color', 'background_color']
  list_filter = ['level']
  search_fields = ['level', 'name']

admin.site.register(models.CustomUser, CustomUserAdmin)
admin.site.register(models.UPLOAD, UploadAdmin)
admin.site.register(models.SERVER_SETTING, ServerSettingAdmin)
admin.site.register(models.LEVEL_RULE, LevelRuleAdmin)