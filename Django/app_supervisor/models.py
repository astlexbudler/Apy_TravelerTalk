from django.db import models
from datetime import datetime

##########
# 모델 정의

# 배너 모델
# 배너 = 메인 페이지 상단 및 하단(또는 사이드)에 노출되는 이미지
# 클릭 시 location 주소를 염(target="_blank")
# clicks는 사용 안함.
class BANNER(models.Model):
  id = models.AutoField(primary_key=True)
  location = models.CharField(max_length=20, help_text="배너 위치(top, side)")
  display_order = models.IntegerField(help_text="배너 표시 순서(숫가가 클수록 먼저 표시)")
  image = models.CharField(max_length=200, help_text="배너 이미지 URL")
  link = models.CharField(max_length=200, help_text="배너 링크 URL")
  clicks = models.TextField(null=True, blank=True, help_text="클릭한 사용자 ID(없으면 공백. ,로 구분)")
  created_dt = models.DateTimeField(auto_now_add=True, help_text="생성일시")
  def save(self, *args, **kwargs):
    if not self.clicks:
      self.clicks = ''
    super(BANNER, self).save(*args, **kwargs)