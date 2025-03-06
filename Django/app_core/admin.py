from django.contrib import admin
from . import models

# ACCOUNT: 계정 테이블
# ACTIVITY: 활동 테이블
# LEVEL_RULE: 레벨 규칙 테이블
# CATEGORY: 카테고리 테이블
# BOARD: 게시판 테이블
# POST: 게시물 테이블
# PLACE_INFO: 여행지 정보 테이블
# COMMENT: 댓글 테이블
# COUPON: 쿠폰 테이블
# MESSAGE: 메시지 테이블
# UPLOAD: 파일 업로드 테이블
# SERVER_SETTING: 서버 설정 테이블
# SERVER_LOG: 서버 로그 테이블
# BANNER: 배너 테이블

class ACCOUNTAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login', 'status', 'note', 'mileage', 'exp', 'tel', 'subsupervisor_permissions', 'level', 'recent_ip')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'status', 'level')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'tel', 'note', 'recent_ip')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'bookmarked_posts')
admin.site.register(models.ACCOUNT, ACCOUNTAdmin)

class ACTIVITYAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'message', 'exp_change', 'mileage_change', 'created_at')
    list_filter = ('account',)
    search_fields = ('message',)
    ordering = ('-created_at',)
admin.site.register(models.ACTIVITY, ACTIVITYAdmin)

class LEVEL_RULEAdmin(admin.ModelAdmin):
    list_display = ('level', 'image', 'text', 'text_color', 'background_color', 'required_exp')
    search_fields = ('text',)
    ordering = ('level',)
admin.site.register(models.LEVEL_RULE, LEVEL_RULEAdmin)

class CATEGORYAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_category', 'name', 'display_weight')
    search_fields = ('name',)
    ordering = ('display_weight',)
admin.site.register(models.CATEGORY, CATEGORYAdmin)

class BOARDAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_board', 'name', 'board_type', 'display_weight')
    search_fields = ('name',)
    ordering = ('display_weight',)
admin.site.register(models.BOARD, BOARDAdmin)

class POSTAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'image', 'view_count', 'like_count', 'search_weight', 'created_at')
    list_filter = ('boards', 'place_info')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
admin.site.register(models.POST, POSTAdmin)

class PLACE_INFOAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'location_info', 'address', 'open_info', 'ad_start_at', 'ad_end_at', 'status', 'note')
    list_filter = ('categories', 'status')
    search_fields = ('location_info', 'address', 'open_info', 'note')
    ordering = ('-ad_start_at',)
admin.site.register(models.PLACE_INFO, PLACE_INFOAdmin)

class COMMENTAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'content', 'created_at')
    search_fields = ('content',)
    ordering = ('-created_at',)
admin.site.register(models.COMMENT, COMMENTAdmin)

class COUPONAdmin(admin.ModelAdmin):
    list_display = ('code', 'related_post', 'create_account', 'own_account', 'name', 'image', 'required_mileage', 'expire_at', 'created_at', 'status', 'note')
    list_filter = ('status',)
    search_fields = ('code', 'name', 'content', 'note')
    ordering = ('-created_at',)
admin.site.register(models.COUPON, COUPONAdmin)

class MESSAGEAdmin(admin.ModelAdmin):
    list_display = ('to_account', 'sender_account', 'include_coupon', 'title', 'image', 'is_read', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
admin.site.register(models.MESSAGE, MESSAGEAdmin)

class UPLOADAdmin(admin.ModelAdmin):
    list_display = ('id', 'file')
admin.site.register(models.UPLOAD, UPLOADAdmin)

class SERVER_SETTINGAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    search_fields = ('name', 'value')
admin.site.register(models.SERVER_SETTING, SERVER_SETTINGAdmin)

class BANNERAdmin(admin.ModelAdmin):
    list_display = ('location', 'image', 'link', 'size', 'display_weight')
    search_fields = ('link',)
    ordering = ('display_weight',)
admin.site.register(models.BANNER, BANNERAdmin)
