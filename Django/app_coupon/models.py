from app_core import models as core_mo
from django.db import models
from datetime import datetime

##########
# 모델 정의

# 쿠폰 모델(미사용 쿠폰)
# 파트너 또는 관리자만 쿠폰 생성 가능. 사용자(user, dame)는 쿠폰을 전달받고 확인 가능.
# 파트너 계정은 쿠폰 사용 처리 가능.
# 사용된 쿠폰은 COUPON_HISTORY 모델로 이동됨.
class COUPON(models.Model):
  id = models.AutoField(primary_key=True)
  code = models.CharField(max_length=20, help_text="쿠폰 코드")
  create_account_id = models.CharField(max_length=60, help_text="쿠폰 생성자 ID(파트너 또는 관리자 ID)")
  own_user_id = models.CharField(max_length=60, help_text="쿠폰 소유자 ID")
  name = models.CharField(max_length=100, help_text="쿠폰 이름(최대 100자)")
  description = models.TextField(help_text="쿠폰 설명")
  images = models.TextField(null=True, blank=True, help_text="쿠폰 이미지 URL(없으면 공백. ,로 구분)")
  post_id = models.CharField(max_length=16, blank=True, null=True, help_text="관련 게시물 ID. 없으면 공백")
  created_dt = models.DateTimeField(auto_now_add=True, help_text="생성일시")
  required_point = models.IntegerField(help_text="필요 포인트")
  def save(self, *args, **kwargs):
    if not self.required_point:
      self.required_point = 0
    if not self.post_id:
      self.post_id = ''
    if not self.images:
      self.images = ''
    super(COUPON, self).save(*args, **kwargs)

# 쿠폰 히스토리 모델
# 사용된 쿠폰 기록 보관. 사용자가 쿠폰을 사용하면 이동됨.
# 삭제되거나 만료 처리된 쿠폰도 이동됨.
# 파트너가 note에 메모를 남길 수 있음. 메모는 파트너만 확인 가능.
class COUPON_HISTORY(models.Model):
  id = models.AutoField(primary_key=True)
  code = models.CharField(max_length=20, help_text="쿠폰 코드")
  create_account_id = models.CharField(max_length=60, help_text="쿠폰 생성자 ID(파트너 또는 관리자 ID)")
  used_user_id = models.CharField(max_length=60, help_text="쿠폰 사용자 ID")
  name = models.CharField(max_length=100, help_text="쿠폰 이름(최대 100자)")
  description = models.TextField(help_text="쿠폰 설명")
  images = models.TextField(null=True, blank=True, help_text="쿠폰 이미지 URL(없으면 공백. ,로 구분)")
  post_id = models.CharField(max_length=16, blank=True, null=True, help_text="관련 게시물 ID. 없으면 공백")
  created_dt = models.DateTimeField(help_text="생성일시")
  used_dt = models.DateTimeField(auto_now_add=True, help_text="사용일시")
  required_point = models.IntegerField(help_text="필요 포인트")
  status = models.CharField(max_length=30, help_text="쿠폰 상태(used, expired, deleted)")
  note = models.TextField(null=True, blank=True, help_text="관리자 또는 파트너 메모")
  def save(self, *args, **kwargs):
    if not self.required_point:
      self.required_point = 0
    if not self.post_id:
      self.post_id = ''
    if not self.note:
      self.note = ''
    if not self.images:
      self.images = ''
    super(COUPON_HISTORY, self).save(*args, **kwargs)