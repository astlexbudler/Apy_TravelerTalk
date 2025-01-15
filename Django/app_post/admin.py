from django.contrib import admin
from . import models

class BoardAdmin(admin.ModelAdmin):
  list_display = ['id', 'name', 'post_type']
  list_filter = ['post_type']
  search_fields = ['name']

class PostAdmin(admin.ModelAdmin):
  list_display = ['id', 'board_id', 'title']
  list_filter = ['board_id']
  search_fields = ['title']

class AdAdmin(admin.ModelAdmin):
  list_display = ['id', 'post_id', 'weight', 'status']
  list_filter = ['post_id', 'status']
  search_fields = ['weight']

class CommentAdmin(admin.ModelAdmin):
  list_display = ['id', 'post_id', 'content']
  list_filter = ['post_id']
  search_fields = ['content']

admin.site.register(models.BOARD, BoardAdmin)
admin.site.register(models.POST, PostAdmin)
admin.site.register(models.AD, AdAdmin)
admin.site.register(models.COMMENT, CommentAdmin)