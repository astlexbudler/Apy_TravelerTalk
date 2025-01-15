from django.db import models
from datetime import datetime

##########
# 모델 정의

# 활동 모델
# 사용자의 활동 기록을 저장
# 각 활동 뵬 포인트 포인트 변동이 있다면, 변동 포인트를 같이 기록
# 형식: [주체] 메시지(예: [자유게시판] hello 게시글을 작성하였습니다.
class ACTIVITY(models.Model):
  id = models.AutoField(primary_key=True)
  user_id = models.CharField(max_length=60, help_text="사용자 ID")
  location = models.CharField(null=True, blank=True, max_length=200, help_text="활동 위치(없으면 공백)")
  message = models.TextField(help_text="활동 내용")
  point_change = models.CharField(null=True, blank=True, help_text="포인트 변동량", max_length=20)
  created_dt = models.DateTimeField(auto_now_add=True, help_text="활동 일시")
  def save(self, *args, **kwargs):
    if not self.location:
      self.location = ''
    if not self.point_change:
      self.point_change = ''
    super(ACTIVITY, self).save(*args, **kwargs)