from django.contrib import admin
from . import models

# ACCOUNT: 계정 테이블
# GROUP: 그룹 테이블
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

admin.site.register(models.ACCOUNT)
#admin.site.register(models.GROUP)
admin.site.register(models.ACTIVITY)
admin.site.register(models.LEVEL_RULE)
admin.site.register(models.CATEGORY)
admin.site.register(models.BOARD)
admin.site.register(models.POST)
admin.site.register(models.PLACE_INFO)
admin.site.register(models.COMMENT)
admin.site.register(models.COUPON)
admin.site.register(models.MESSAGE)
admin.site.register(models.UPLOAD)
admin.site.register(models.SERVER_SETTING)
admin.site.register(models.SERVER_LOG)
admin.site.register(models.BANNER)