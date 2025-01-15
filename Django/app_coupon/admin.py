from django.contrib import admin
from . import models

class CouponAdmin(admin.ModelAdmin):
  list_display = ['id', 'code', 'name', 'create_account_id', 'own_user_id', 'created_dt', 'required_point']
  list_filter = ['create_account_id', 'own_user_id']
  search_fields = ['code', 'name']

class CouponHistoryAdmin(admin.ModelAdmin):
  list_display = ['id', 'code', 'name', 'create_account_id', 'used_user_id', 'created_dt', 'used_dt', 'status']
  list_filter = ['create_account_id', 'used_user_id', 'status']
  search_fields = ['code', 'name']

admin.site.register(models.COUPON, CouponAdmin)
admin.site.register(models.COUPON_HISTORY, CouponHistoryAdmin)