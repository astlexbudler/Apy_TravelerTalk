from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from datetime import datetime
import os

####################
# TABLE
# ACCOUNT: 계정 테이블
# GROUP: 그룹 테이블(장고 기본)
# ACTIVITY: 활동 테이블
# LEVEL_RULE: 레벨 규칙 테이블
# POST: 게시물 테이블
# PLACE_INFO: 여행지 정보 테이블
# COMMENT: 댓글 테이블
# COUPON: 쿠폰 테이블
# MESSAGE: 메시지 테이블
# SERVER_SETTING: 서버 설정 테이블
# UPLOAD: 파일 업로드 테이블
# BANNER: 배너 테이블
# STATISTIC: 통계 테이블
# Blocked_IP: 차단 IP 테이블

# TREE
# BOARD: 게시판 트리
# CATEGORY: 카테고리 트리

def upload_to(instance, filename):  # 파일 업로드 경로 및 파일명 설정
    _, ext = os.path.splitext(filename)
    new_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}{ext}" # 현재 시간을 이용한 파일명 생성
    return os.path.join(new_filename)

####################
# ACCOUNT: 계정 테이블
class ACCOUNT(AbstractUser):
  # id = models.AutoField(primary_key=True) 데이터베이스 식별용 아이디
  # username = models.CharField(max_length=150, unique=True) 로그인 시 사용하는 아이디
  # password = models.CharField(max_length=128)
  # first_name = models.CharField(max_length=30) # 닉네임
  # last_name = models.CharField(max_length=150) # 파트너 업체명
  # email = models.EmailField(max_length=254) # 파트너 이메일
  # is_active = models.BooleanField(default=True) # 계정 활성화 여부
  # is_staff = models.BooleanField(default=False) # 관리자 여부(최상위 관리자만 True)
  # is_superuser = models.BooleanField(default=False) # 최상위 관리자 여부(최상위 관리자만 True)
  # date_joined = models.DateTimeField(auto_now_add=True)
  # last_login = models.DateTimeField(auto_now=True)
  # groups = models.ManyToManyField(Group) # 그룹(user, dame, partner, subsupervisor, supervisor 중 하나)
  status = models.CharField(max_length=20, help_text='active=활성, pending=승인 대기, deleted=삭제, bhide=정지')
  note = models.TextField(blank=True, help_text='관리자 메모')
  mileage = models.IntegerField(help_text='쿠폰 마일리지', default=0)
  exp = models.IntegerField(help_text='레벨업 경험치', default=0)
  tel = models.CharField(blank=True, max_length=20, help_text='연락처')
  subsupervisor_permissions = models.CharField(blank=True, max_length=100, help_text='account=계정 관리 권한, post=게시글 관리 권한, coupon=쿠폰 관리 권한, message=메시지 관리 권한, banner=배너 관리 권한, setting=설정 권한)')
  bookmarked_posts = models.ManyToManyField('POST', help_text='즐겨찾기 여행지', related_name='account_bookmarked_places')
  level = models.ForeignKey('LEVEL_RULE', null=True, help_text='사용자 레벨', related_name='account_level', on_delete=models.SET_NULL)
  recent_ip = models.CharField(max_length=20, blank=True, help_text='최근 접속 IP')

# GROUP: 그룹 테이블
# class GROUP(models.Model):
# name = models.CharField(primary_key=True) # 그룹 이름(user, dame, partner, subsupervisor, supervisor)
# permissions = models.ManyToManyField(Permission)

# ACTIVITY: 활동 테이블
class ACTIVITY(models.Model):
  account = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, help_text='계정', related_name='activity_account')
  message = models.CharField(max_length=200, help_text='활동 메시지')
  exp_change = models.IntegerField(help_text='경험치 변화', default=0)
  mileage_change = models.IntegerField(help_text='마일리지 변화', default=0)
  created_at = models.DateTimeField(auto_now_add=True, help_text='활동 일시')

# LEVEL_RULE: 레벨 규칙 테이블
class LEVEL_RULE(models.Model):
  level = models.IntegerField(primary_key=True)
  image = models.FileField(upload_to=upload_to, null=True, help_text='레벨 이미지. 이미지가 없다면, 아래 텍스트 색상과 배경 색상을 사용')
  text = models.CharField(max_length=20, blank=True, help_text='레벨 이름. 이미지가 있다면 사용하지 않음')
  text_color = models.CharField(max_length=20, blank=True, help_text='레벨 텍스트 색상. 이미지가 있다면 사용하지 않음')
  background_color = models.CharField(max_length=20, blank=True, help_text='레벨 배경 색상. 이미지가 있다면 사용하지 않음')
  required_exp = models.IntegerField(help_text='레벨업 필요 경험치')

# POST: 게시물 테이블
class POST(models.Model):
  author = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, null=True, help_text='게시글 작성자', related_name='post_author')
  boards = models.ManyToManyField('BOARD', help_text='게시판', related_name='post_boards')
  related_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, help_text='관련 게시글(리뷰 게시글일 경우, 리뷰 또는 쿠폰 게시글일 경우, 대상 여행지 게시글)', related_name='post_related_post')
  place_info = models.ForeignKey('PLACE_INFO', on_delete=models.CASCADE, null=True, help_text='여행지 정보', related_name='post_place_info')
  include_coupons = models.ManyToManyField('COUPON', help_text='포함된 쿠폰', related_name='post_include_coupons')
  title = models.CharField(max_length=100, help_text='제목')
  image = models.FileField(upload_to=upload_to, null=True, help_text='대표 이미지')
  content = models.TextField(help_text='내용', null=True)
  view_count = models.IntegerField(help_text='조회수', default=0)
  like_count = models.IntegerField(help_text='좋아요 수', default=0)
  search_weight = models.IntegerField(help_text='검색 가중치', default=0)
  hide = models.BooleanField(help_text='숨김 여부', default=False)
  created_at = models.DateTimeField(auto_now_add=True, help_text='작성 일시')

# PLACE_INFO: 여행지 정보 테이블
class PLACE_INFO(models.Model):
  post = models.ForeignKey('POST', on_delete=models.CASCADE, help_text='게시글', related_name='place_post')
  categories = models.ManyToManyField('CATEGORY', help_text='카테고리', related_name='place_categories')
  location_info = models.CharField(max_length=100, help_text='위치 정보')
  open_info = models.CharField(max_length=100, help_text='영업 정보')
  address = models.CharField(max_length=200, help_text='주소')
  ad_start_at = models.DateTimeField(auto_now_add=True, help_text='광고 시작 일시')
  ad_end_at = models.DateTimeField(auto_now_add=True, help_text='광고 종료 일시')
  status = models.CharField(max_length=20, default='hide', help_text='상태(hide, active, pending, ad)')
  note = models.TextField(help_text='관리자 메모')

# COMMENT: 댓글 테이블
class COMMENT(models.Model):
  post = models.ForeignKey('POST', on_delete=models.CASCADE, help_text='게시글', related_name='comment_post', null=True)
  parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, help_text='상위 댓글', related_name='comment_parent_comment')
  author = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, help_text='작성자', related_name='comment_author')
  content = models.TextField(help_text='내용')
  hide = models.BooleanField(help_text='숨김 여부', default=False)
  created_at = models.DateTimeField(auto_now_add=True, help_text='작성 일시')

# COUPON: 쿠폰 테이블
class COUPON(models.Model):
  code = models.CharField(max_length=20, primary_key=True, help_text='쿠폰 코드')
  related_post = models.ForeignKey('POST', on_delete=models.CASCADE, null=True, help_text='게시글', related_name='coupon_post')
  create_account = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, help_text='생성자', related_name='coupon_create_account')
  own_account = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, null=True, help_text='소유 계정', related_name='coupon_own_account')
  name = models.CharField(max_length=100, help_text='쿠폰 이름')
  image = models.FileField(upload_to=upload_to, null=True, help_text='이미지')
  content = models.TextField(help_text='내용', null=True)
  required_mileage = models.IntegerField(help_text='필요 마일리지', default=0)
  expire_at = models.DateTimeField(help_text='만료 일시')
  created_at = models.DateTimeField(auto_now_add=True, help_text='생성 일시')
  status = models.CharField(max_length=20, default='active', help_text='상태(active, used, expired, deleted)')
  note = models.TextField(help_text='관리자 메모')

# MESSAGE: 메시지 테이블
class MESSAGE(models.Model):
  receive = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, help_text='받는 사람', related_name='message_receive', null=True) # null=True: 관리자 메시지
  sender = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, help_text='보낸 사람', related_name='message_sender', null=True) # null=True: 관리자 메시지
  include_coupon = models.ForeignKey('COUPON', null=True, help_text='포함된 쿠폰', related_name='message_include_coupon', on_delete=models.SET_NULL)
  title = models.CharField(max_length=100, help_text='제목')
  image = models.FileField(upload_to=upload_to, null=True, help_text='이미지')
  content = models.TextField(help_text='내용', null=True)
  message_type = models.CharField(max_length=20, help_text='user_question=사용자 문의, partner_question=파트너 문의, request_ad=광고 요청, request_coupon=쿠폰 요청')
  is_read = models.BooleanField(default=False, help_text='읽음 여부')
  created_at = models.DateTimeField(auto_now_add=True, help_text='생성 일시')

# SERVER_SETTING: 서버 설정 테이블
class SERVER_SETTING(models.Model):
  name = models.CharField(max_length=100, primary_key=True, help_text='설정 이름')
  value = models.TextField(help_text='설정 값')

# UPLOAD: 파일 업로드 테이블
class UPLOAD(models.Model):
  file = models.FileField(upload_to=upload_to, help_text='파일')

# BANNER: 배너 테이블
class BANNER(models.Model):
  location = models.CharField(max_length=20, help_text='top=상단, side=하단, post=게시글')
  image = models.FileField(upload_to=upload_to, help_text='이미지')
  link = models.CharField(max_length=300, help_text='링크')
  status = models.CharField(max_length=20, help_text='full=최대 크기, half=중간 크기, none=미표시')
  display_weight = models.IntegerField(help_text='표시 순서', default=0)

# STATISTIC: 통계 테이블
class STATISTIC(models.Model):
  name = models.CharField(max_length=100, help_text='통계 이름')
  value = models.IntegerField(help_text='통계 값', default=0)
  date = models.DateTimeField(auto_now_add=True, help_text='통계 일시')

# Blocked_IP: 차단 IP 테이블
class BLOCKED_IP(models.Model):
  ip = models.CharField(max_length=20, help_text='차단 IP')


####################
# BOARD: 게시판 테이블
class BOARD(models.Model):
  parent_board = models.ForeignKey('self', on_delete=models.CASCADE, null=True, help_text='상위 게시판', related_name='board_parent_board')
  display_groups = models.ManyToManyField(Group, help_text='게시판 입장 그룹', related_name='board_display_groups')
  write_groups = models.ManyToManyField(Group, help_text='게시글 작성 그룹', related_name='board_write_groups')
  comment_groups = models.ManyToManyField(Group, help_text='댓글 작성 그룹', related_name='board_comment_groups')
  level_cut = models.IntegerField(help_text='게시글 접근 레벨 제한', default=0)
  name = models.CharField(max_length=100, help_text='게시판 이름')
  # attendance=출석 게시판, greeting=인사 게시판, anonymous=익명 게시판, qna=질문 게시판, travel=여행지 정보 게시판, coupon=쿠폰 게시판, review=리뷰 게시판, board=일반 게시판, gallery=갤러리 게시판
  board_type = models.CharField(max_length=20, help_text='게시판 타입')
  display_weight = models.IntegerField(help_text='표시 순서', default=0)

# CATEGORY: 카테고리 테이블
class CATEGORY(models.Model):
  parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, help_text='상위 카테고리', related_name='category_parent_category')
  name = models.CharField(max_length=100, help_text='카테고리 이름')
  display_weight = models.IntegerField(help_text='표시 순서', default=0)