from django.db import models
from django.contrib.auth.models import AbstractUser, Group

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
# BLOCKED_IP: 차단 IP 테이블

# TREE
# BOARD: 게시판 트리
# CATEGORY: 카테고리 트리

####################
# ACCOUNT: 계정 테이블
class ACCOUNT(AbstractUser):
  # id = models.AutoField(primary_key=True)
  # username = models.CharField(max_length=150, unique=True) 로그인 시 사용하는 아이디
  # password = models.CharField(max_length=128)
  # first_name = models.CharField(max_length=30) # 닉네임
  # last_name = models.CharField(max_length=150) # 파트너 업체명(게시글 여행지에서는 이걸 닉네임으로 사용)
  # email = models.EmailField(max_length=254) # 파트너 이메일
  # is_active = models.BooleanField(default=True) # 계정 활성화 여부
  # is_staff = models.BooleanField(default=False) # 관리자 여부(최상위 관리자만 True)
  # is_superuser = models.BooleanField(default=False) # 최상위 관리자 여부(최상위 관리자만 True)
  # date_joined = models.DateTimeField(auto_now_add=True)
  # last_login = models.DateTimeField(auto_now=True)
  # groups = models.ManyToManyField(Group) # 그룹(user, dame, partner, subsupervisor, supervisor 중 하나)
  status = models.CharField(max_length=100, help_text='계정 상태(active, pending, deleted, blocked)')
  note = models.TextField(blank=True, help_text='관리자 메모')
  mileage = models.IntegerField(help_text='쿠폰 마일리지', default=0)
  exp = models.IntegerField(help_text='레벨업 경험치', default=0)
  tel = models.CharField(blank=True, max_length=20, help_text='연락처')
  subsupervisor_permissions = models.CharField(blank=True, max_length=200, help_text='관리자 권한(account, post, coupon, message, banner, setting)')
  bookmarked_places = models.ManyToManyField('POST', help_text='즐겨찾기 여행지', related_name='account_bookmarked_places')
  level = models.ForeignKey('LEVEL_RULE', null=True, help_text='사용자 레벨', related_name='account_level', on_delete=models.SET_NULL)
  recent_ip = models.CharField(max_length=20, blank=True, help_text='최근 접속 IP')

# GROUP: 그룹 테이블
# class GROUP(models.Model):
# name = models.CharField(primary_key=True) # 그룹 이름(user, dame, partner, subsupervisor, supervisor)
# permissions = models.ManyToManyField(Permission)

# ACTIVITY: 활동 테이블
class ACTIVITY(models.Model):
  account = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, help_text='계정', related_name='activity_account')
  message = models.TextField(help_text='활동 내용')
  exp_change = models.IntegerField(help_text='경험치 변화', default=0)
  mileage_change = models.IntegerField(help_text='마일리지 변화', default=0)
  created_at = models.DateTimeField(auto_now_add=True, help_text='활동 일시')

# LEVEL_RULE: 레벨 규칙 테이블
class LEVEL_RULE(models.Model):
  level = models.IntegerField(primary_key=True)
  image = models.FileField(upload_to='level/', null=True, help_text='레벨 이미지. 이미지가 없다면, 아래 텍스트 색상과 배경 색상을 사용')
  text = models.CharField(max_length=20, blank=True, help_text='레벨 이름. 이미지가 있다면 사용하지 않음')
  text_color = models.CharField(max_length=20, blank=True, help_text='레벨 텍스트 색상. 이미지가 있다면 사용하지 않음')
  background_color = models.CharField(max_length=20, blank=True, help_text='레벨 배경 색상. 이미지가 있다면 사용하지 않음')
  required_exp = models.IntegerField(help_text='레벨업 필요 경험치')

# POST: 게시물 테이블
class POST(models.Model):
  author = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, null=True, help_text='작성자', related_name='post_author')
  boards = models.ManyToManyField('BOARD', help_text='게시판', related_name='post_boards')
  related_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, help_text='관련 게시글(리뷰 게시글일 경우, 리뷰 또는 쿠폰 게시글일 경우, 대상 여행지 게시글)', related_name='post_related_post')
  place_info = models.ForeignKey('PLACE_INFO', on_delete=models.CASCADE, null=True, help_text='여행지 정보', related_name='post_place_info')
  title = models.CharField(max_length=100, help_text='제목')
  image = models.FileField(upload_to='post/', null=True, help_text='대표 이미지')
  content = models.TextField(help_text='내용(ToastfulEditor)', null=True)
  view_count = models.IntegerField(help_text='조회수', default=0)
  like_count = models.IntegerField(help_text='좋아요 수', default=0)
  search_weight = models.IntegerField(help_text='검색 가중치', default=0)
  created_at = models.DateTimeField(auto_now_add=True, help_text='작성 일시')

# PLACE_INFO: 여행지 정보 테이블
class PLACE_INFO(models.Model):
  post = models.ForeignKey('POST', on_delete=models.CASCADE, help_text='게시글', related_name='place_post')
  categories = models.ManyToManyField('CATEGORY', help_text='카테고리', related_name='place_categories')
  location_info = models.CharField(max_length=200, help_text='위치 정보')
  address = models.CharField(max_length=200, help_text='주소')
  open_info = models.CharField(max_length=200, help_text='영업 정보')
  ad_start_at = models.DateTimeField(auto_now_add=True, help_text='광고 시작 일시')
  ad_end_at = models.DateTimeField(auto_now_add=True, help_text='광고 종료 일시')
  status = models.CharField(max_length=20, default='normal', help_text='상태(writing, active, pending, ad, blocked)')
  note = models.TextField(help_text='관리자 메모')

# COMMENT: 댓글 테이블
class COMMENT(models.Model):
  post = models.ForeignKey('POST', on_delete=models.CASCADE, help_text='게시글', related_name='comment_post')
  author = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, help_text='작성자', related_name='comment_author')
  content = models.TextField(help_text='내용')
  created_at = models.DateTimeField(auto_now_add=True, help_text='작성 일시')

# COUPON: 쿠폰 테이블
class COUPON(models.Model):
  code = models.CharField(max_length=20, primary_key=True, help_text='쿠폰 코드')
  related_post = models.ForeignKey('POST', on_delete=models.CASCADE, null=True, help_text='게시글', related_name='coupon_post')
  create_account = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, help_text='생성자', related_name='coupon_create_account')
  own_account = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, null=True, help_text='소유 계정', related_name='coupon_own_account')
  name = models.CharField(max_length=100, help_text='쿠폰 이름')
  image = models.FileField(upload_to='coupon/', null=True, help_text='이미지')
  content = models.TextField(help_text='내용(ToastfulEditor)', null=True)
  required_mileage = models.IntegerField(help_text='필요 마일리지', default=0)
  expire_at = models.DateTimeField(help_text='만료 일시')
  created_at = models.DateTimeField(auto_now_add=True, help_text='생성 일시')
  status = models.CharField(max_length=20, default='active', help_text='상태(active, used, expired, deleted)')
  note = models.TextField(help_text='관리자 메모')

# MESSAGE: 메시지 테이블
class MESSAGE(models.Model):
  to_account = models.CharField(max_length=60, help_text='받는 사람(관리자일 경우 supervisor, 게스트일 경우, guest_id, 그 외 계정일 경우, 계정 id)')
  sender_account = models.CharField(max_length=60, help_text='보낸 사람(관리자일 경우 supervisor, 게스트일 경우, guest_id, 그 외 계정일 경우, 계정 id)')
  include_coupon = models.ForeignKey('COUPON', null=True, help_text='포함된 쿠폰', related_name='message_include_coupon', on_delete=models.SET_NULL)
  title = models.CharField(max_length=100, help_text='제목')
  image = models.FileField(upload_to='message/', null=True, help_text='이미지')
  content = models.TextField(help_text='내용(ToastfulEditor)', null=True)
  is_read = models.BooleanField(default=False, help_text='읽음 여부')
  created_at = models.DateTimeField(auto_now_add=True, help_text='생성 일시')

# SERVER_SETTING: 서버 설정 테이블
class SERVER_SETTING(models.Model):
  name = models.CharField(max_length=100, primary_key=True, help_text='설정 이름')
  value = models.TextField(help_text='설정 값')

# UPLOAD: 파일 업로드 테이블
class UPLOAD(models.Model):
  file = models.FileField(upload_to='setting/', help_text='파일')

# BANNER: 배너 테이블
class BANNER(models.Model):
  location = models.CharField(max_length=20, help_text='위치(top, side)')
  image = models.FileField(upload_to='banner/', help_text='이미지')
  link = models.CharField(max_length=300, help_text='링크')
  size = models.CharField(max_length=20, help_text='크기(half, full)')
  display_weight = models.IntegerField(help_text='표시 순서', default=0)

# STATISTIC: 통계 테이블
class STATISTIC(models.Model):
  name = models.CharField(max_length=100, help_text='통계 이름')
  value = models.IntegerField(help_text='통계 값', default=0)
  date = models.DateTimeField(auto_now_add=True, help_text='통계 일시')

# BLOCKED_IP: 차단 IP 테이블
class BLOCKED_IP(models.Model):
  ip = models.CharField(max_length=20, help_text='차단 IP')


####################
# BOARD: 게시판 테이블
class BOARD(models.Model):
  parent_board = models.ForeignKey('self', on_delete=models.CASCADE, null=True, help_text='상위 게시판', related_name='board_parent_board')
  display_groups = models.ManyToManyField(Group, help_text='게시판 표시 그룹', related_name='board_display_groups')
  enter_groups = models.ManyToManyField(Group, help_text='게시글 접근 그룹', related_name='board_enter_groups')
  write_groups = models.ManyToManyField(Group, help_text='게시글 작성 그룹', related_name='board_write_groups')
  comment_groups = models.ManyToManyField(Group, help_text='댓글 작성 그룹', related_name='board_comment_groups')
  level_cut = models.IntegerField(help_text='게시글 접근 레벨 제한', default=0)
  name = models.CharField(max_length=100, help_text='게시판 이름')
  # attendance: 출석 게시판. *특수 게시판
  # greeting: 인사 게시판. *특수 게시판
  # anonymous: 익명 게시판. 모두 글 작성 가능.*특수 게시판
  # qna: 질문 게시판. 모두 글 작성 가능. 댓글 작성 대신 답변 생성이라고 표시.*특수 게시판
  # travel: 여행지 정보 게시판. 파트너만 글 작성 가능.*특수 게시판
  # coupon: 쿠폰 게시판. 파트너와 관리자만 글 작성 가능.*특수 게시판
  # review: 리뷰 게시판. 사용자만 글 작성 가능.*특수 게시판
  # tree: 다른 게시판을 포함하는 게시판. 글 작성 불가.
  # board: 일반 게시판. 모두 글 작성 가능.
  board_type = models.CharField(max_length=20, help_text='게시물 타입(tree, travel, event, review, board, attendance, greeting, anonymous, qna, coupon)')
  display_weight = models.IntegerField(help_text='표시 순서', default=0)

# CATEGORY: 카테고리 테이블
class CATEGORY(models.Model):
  parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, help_text='상위 카테고리', related_name='category_parent_category')
  name = models.CharField(max_length=100, help_text='카테고리 이름')
  display_weight = models.IntegerField(help_text='표시 순서', default=0)