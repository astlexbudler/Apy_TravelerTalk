from django.db import models
import os
from datetime import datetime
import random
import string
from django.contrib.auth.models import AbstractUser

def random_id(length): # 랜덤 아이디 생성(알파벳 + 숫자) *첫 글자는 반드시 알파벳
  return ''.join(random.choices(string.ascii_letters, k=1)) + ''.join(random.choices(string.ascii_letters + string.digits, k=length-1))

def upload_to(instance, filename): # 파일 업로드 경로
  _, ext = os.path.splitext(filename)
  new_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}{ext}"
  return os.path.join("traveltalk/", new_filename)

##########
# 모델 정의

# 파일 업로드 모델
# 업로드된 파일은 /media/traveltalk/ 경로에 저장됨. 파일명은 업로드 시간으로 생성됨.
class UPLOAD(models.Model):
  file = models.FileField(upload_to=upload_to)

# 사용자 모델
# Django 기본 사용자 모델(AbstractUser)을 상속받아 커스텀 사용자 모델을 정의함.
# request.user로 접근 가능. (ex. request.user.username, request.user.account_type)
class CustomUser(AbstractUser):
  # id = models.AutoField(primary_key=True)
  # username = models.CharField(max_length=150, unique=True)
  # password = models.CharField(max_length=128)
  # first_name = models.CharField(max_length=30) nickname으로 사용
  # last_name = models.CharField(max_length=150) (사용 안함)
  # email = models.EmailField(max_length=254) (사용 안함)
  # is_active = models.BooleanField(default=True) # 계정 활성화 여부. False면 로그인 불가.
  # is_staff = models.BooleanField(default=False)pyth
  # is_superuser = models.BooleanField(default=False)
  # date_joined = models.DateTimeField(auto_now_add=True)
  # last_login = models.DateTimeField(auto_now=True)
  # groups = models.ManyToManyField(Group)
  account_type = models.CharField(max_length=20, help_text='계정 유형(user, dame, partner, supervisor, sub_supervisor, admin)')
  status = models.CharField(max_length=20, help_text='계정 상태(active, pending, sleeping, deleted, blocked, banned)') # 계정 상태. active, pending, deleted만 사용.
  note = models.TextField(null=True, blank=True, help_text='관리자 메모(없으면 공백)')
  user_usable_point = models.IntegerField(help_text='사용 가능한 포인트')
  user_level_point = models.IntegerField(help_text='레벨업 포인트')
  user_level = models.IntegerField(help_text='사용자 레벨')
  user_bookmarks = models.TextField(null=True, blank=True, help_text='북마크한 게시물 ID(없으면 공백. ,로 구분)')
  partner_tel = models.CharField(null=True, blank=True, max_length=20, help_text='파트너 연락처(없으면 공백)')
  partner_address = models.CharField(null=True, blank=True, max_length=200, help_text='파트너 주소(없으면 공백)')
  partner_categories = models.CharField(null=True, blank=True, max_length=200, help_text='파트너 업종 카테고리(없으면 공백)')
  supervisor_permissions = models.CharField(max_length=200, null=True, blank=True, help_text='관리자 권한(없으면 공백. ,로 구분. user(사용자 관리), partner(파트너 관리), supervisor(관리자 관리), post(게시물 관리), coupon(쿠폰 관리), message(메시지 관리), setting(설정 관리))')
  def save(self, *args, **kwargs):
    if not self.user_usable_point:
      self.user_usable_point = 0
    if not self.user_level_point:
      self.user_level_point = 0
    if not self.user_level:
      self.user_level = 1
    if not self.user_bookmarks:
      self.user_bookmarks = ''
    if not self.partner_tel:
      self.partner_tel = ''
    if not self.partner_address:
      self.partner_address = ''
    if not self.partner_categories:
      self.partner_categories = ''
    if not self.supervisor_permissions:
      self.supervisor_permissions = ''
    if not self.note:
      self.note = ''
    super(CustomUser, self).save(*args, **kwargs)
  def __str__(self):
    return self.username

# 서버 설정 모델
# 아래와 같은 설정을 저장함.
# site_name(사이트 이름) 사이트 이름, 바로가기 이름 및 시스템 이름 등 다양한 곳에서 사용됨.
# site_logo(사이트 로고 URL) 사이트의 로고 이미지 경로
# site_favicon(파비콘) 파비콘 이미지 경로
# company_name(회사명) 회사명. footer 및 contact 등에 사용됨.
# company_address(회사 주소) 회사 주소. footer 및 contact 등에 사용됨.
# company_tel(회사 연락처) 회사 연락처. footer 및 contact 등에 사용됨.
# company_email(회사 이메일) 회사 이메일. footer 및 contact 등에 사용됨.
# social_network_x(x 주소) 소셜 네트워크 주소
# social_network_meta(meta 주소) 소셜 네트워크 주소
# social_network_insta(인스타 주소) 소셜 네트워크 주소
# register_point(회원가입 포인트) 회원가입 시 지급되는 포인트(사용자 및 여성 회원만 해당)
# attend_point(출석 포인트) 출석 시 지급되는 포인트(1등은 2배, 2등은 1.5배, 3등은 1.2배 지급)
# post_point(게시물 작성 포인트) 게시물 작성 시 지급되는 포인트
# comment_point(댓글 작성 포인트) 댓글 작성 시 지급되는 포인트
# terms(이용약관) 이용약관 내용. terms 페이지에서 사용됨.
class SERVER_SETTING(models.Model):
  id = models.CharField(max_length=100, help_text="설정 이름", primary_key=True)
  value = models.TextField(help_text="설정 값")
  class MetaData:
    api_permission = {
      "id": "RW",
      "value": "RW"
    }

# 레벨 규칙 모델
# 사용자 레벨업에 필요한 포인트 및 레벨 이름, 뱃지 색상을 저장함.
# 한번 레벨업이 되면, required_point 값이 수정되어도 레벨이 다시 내려가지는 않음.
class LEVEL_RULE(models.Model):
  level = models.IntegerField(help_text="레벨", primary_key=True)
  text_color = models.CharField(max_length=20, help_text="레벨 텍스트 색상")
  background_color = models.CharField(max_length=20, help_text="레벨 배경 색상")
  name = models.CharField(max_length=20, help_text="레벨 이름")
  required_point = models.IntegerField(help_text="필요 포인트(한번 레벨업이 되면, 이 값이 수정되어도 레벨이 다시 내려가지는 않음.)")