from app_core import models as core_mo
from django.db import models
from datetime import datetime

##########
# 모델 정의

# 메시지 모델
# guest(비회원)을 포함한 모든 사용자가 메시지를 주고 받을 수 있음.
# 관리자에게 보내는 메세지는 receiver_id를 'supervisor'로 설정.
# guest는 receiver_id를 별도의 'guest_id'로 설정. guest_id는 세션별로 생성됨.
# 메세지에는 최대 1개의 이미지와 쿠폰을 담아서 보낼 수 있음.
# 쿠폰을 사용자가 받고 나면, include_coupon 필드의 값이 ''로 변경됨.
class MESSAGE(models.Model):
  id = models.AutoField(primary_key=True)
  sender_id = models.CharField(max_length=60, help_text="보낸 사람 ID(관리자일경우 supervisor)")
  receiver_id = models.CharField(max_length=60, help_text="받는 사람 ID(관리자일경우 supervisor)")
  title = models.CharField(max_length=100, help_text="제목(최대 100자)")
  content = models.TextField(help_text="내용")
  send_dt = models.DateTimeField(auto_now_add=True, help_text="보낸 일시")
  read_dt = models.DateTimeField(null=True, blank=True, help_text="읽은 일시(읽지 않았으면 공백)")
  include_coupon = models.CharField(null=True, blank=True, max_length=20, help_text="포함된 쿠폰 코드(없으면 공백)")
  images = models.TextField(null=True, blank=True, help_text="이미지 URL(없으면 공백. ,로 구분)")
  def save(self, *args, **kwargs):
    if not self.include_coupon:
      self.include_coupon = ''
    if not self.images:
      self.images = ''
    super(MESSAGE, self).save(*args, **kwargs)
