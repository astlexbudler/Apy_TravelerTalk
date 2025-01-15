import datetime
from django.db import models

##########
# 모델 정의
class BOARD(models.Model):  # 게시판 모델
  id = models.AutoField(primary_key=True)
  parent_id = models.CharField(null=True, blank=True, help_text="상위 게시판 ID(없으면 공백)", max_length=16)
  name = models.CharField(max_length=100, help_text="게시판 이름(최대 100자)")
  post_type = models.CharField(max_length=20, help_text="게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)")
  display_permissions = models.CharField(null=True, blank=True, max_length=100, help_text="게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)") # 사용 안함
  enter_permissions = models.CharField(null=True, blank=True, max_length=100, help_text="게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)")
  write_permissions = models.CharField(null=True, blank=True, max_length=100, help_text="게시판 작성 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)")
  comment_permissions = models.CharField(null=True, blank=True, max_length=100, help_text="게시판 댓글 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)")
  def save(self, *args, **kwargs):
    if not self.parent_id:
      self.parent_id = ''
    if not self.display_permissions:
      self.display_permissions = ''
    if not self.enter_permissions:
      self.enter_permissions = ''
    if not self.write_permissions:
      self.write_permissions = ''
    if not self.comment_permissions:
      self.comment_permissions = ''
    super(BOARD, self).save(*args, **kwargs)

class POST(models.Model):  # 게시물 모델
  id = models.AutoField(primary_key=True)
  board_id = models.CharField(max_length=16, help_text="게시판 ID")
  author_id = models.CharField(max_length=60, help_text="작성자 ID")
  target_post_id = models.CharField(null=True, blank=True, max_length=16, help_text="대상 게시물 ID(없으면 공백)")
  ad_id = models.CharField(null=True, blank=True, max_length=16, help_text="광고 ID(없으면 공백)")
  title = models.CharField(max_length=100, help_text="제목(최대 100자)")
  content = models.TextField(help_text="내용")
  images = models.TextField(null=True, blank=True, help_text="이미지 URL(없으면 공백. ,로 구분)")
  created_dt = models.DateTimeField(auto_now_add=True, help_text="작성일시")
  views = models.TextField(null=True, blank=True, help_text="조회한 사용자 ID(없으면 공백. ,로 구분)")
  bookmarks = models.TextField(null=True, blank=True, help_text="북마크한 사용자 ID(없으면 공백. ,로 구분)")
  weight = models.IntegerField(help_text="가중치(이 값이 높을수록 상위에 표시)")
  def save(self, *args, **kwargs):
    if not self.target_post_id:
      self.target_post_id = ''
    if not self.ad_id:
      self.ad_id = ''
    if not self.images:
      self.images = ''
    if not self.views:
      self.views = ''
    if not self.bookmarks:
      self.bookmarks = ''
    if not self.weight:
      self.weight = 0
    super(POST, self).save(*args, **kwargs)

class AD(models.Model):  # 광고 모델
  id = models.AutoField(primary_key=True)
  post_id = models.CharField(max_length=16, help_text="광고 게시물 ID")
  start_dt = models.DateTimeField(auto_now_add=True, max_length=20, help_text="시작일시. 이 날짜가 지나면 광고가 시작됩니다.")
  end_dt = models.DateTimeField(auto_now_add=True, max_length=20, help_text="종료일시. 이 날짜가 지나면 상태가 expired로 변경됩니다.")
  status = models.CharField(max_length=20, help_text="광고 상태(active, expired)")
  weight = models.IntegerField(help_text="검색 가중치(이 값이 높을수록 검색 결과 상위에 표시)")
  note = models.TextField(null=True, blank=True, help_text="관리자 메모")
  def save(self, *args, **kwargs):
    if not self.note:
      self.note = ''
    super(AD, self).save(*args, **kwargs)

class COMMENT(models.Model):  # 댓글 모델
  id = models.AutoField(primary_key=True)
  post_id = models.CharField(max_length=16, help_text="게시물 ID")
  author_id = models.CharField(max_length=60, help_text="작성자 ID")
  target_comment_id = models.CharField(null=True, blank=True, max_length=16, help_text="대상 댓글 ID(없으면 공백)")
  content = models.TextField(help_text="내용")
  created_dt = models.DateTimeField(auto_now_add=True, help_text="작성일시")
  def save(self, *args, **kwargs):
    if not self.target_comment_id:
      self.target_comment_id = ''
    super(COMMENT, self).save(*args, **kwargs)

