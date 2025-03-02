from django.urls import path
from django.urls import re_path
from django.views.static import serve
from django.conf import settings
from django.urls import include

from . import views as v
from app_api import apis as a

urlpatterns = [

  # views as v
  # 관리자 로그인
  path('', v.login, name='login'),

  # 관리자 메인 페이지
  # 계정 관리, 게시글 관리, 쿠폰 관리, 메세지 관리, 배너 관리, 설정 메뉴 제공
  path('supervisor/supervisor', v.index, name='index'),

  # 계정 관리 페이지
  # 사용자 계정 종류 별 계정 정보 제공. 비밀번호 초기화 및 계정 삭제 기능 제공
  # account_type 별로 별도의 탭 제공.
  # 관리자 아이디 생성 기능 제공(최상위 관리자만 관리자 아이디 생성 가눙)
  # 사용자 정보 수정 기능 제공(사용자 비밀번호 덮어쓰기 기능 제공)
  path('supervisor/account', v.account, name='account'),

  # 프로필
  path('supervisor/account/profile', v.profile, name='profile'),

  # 활동
  path('supervisor/account/activity', v.activity, name='activity'),

  # 게시글 관리 페이지
  # 게시글 목록 및 게시글 삭제 기능 제공
  # 게시글 수정 페이지로 이동 가능
  # 간단하게 게시글 정보 조회
  path('supervisor/post', v.post, name='post'),

  # 게시글 수정 페이지
  path('supervisor/post/edit', v.post_edit, name='post_edit'),

  # 여행지 게시글 관리 페이지
  # 여행지 게시글 목록 및 여행지 게시글 삭제 기능 제공
  # 여행지 게시글 수정 페이지로 이동 가능
  # 간단하게 여행지 게시글 정보 조회
  path('supervisor/travel', v.travel, name='travel'),

  # 여행지 게시글 수정 페이지
  path('supervisor/travel/edit', v.travel_edit, name='travel_edit'),

  # 쿠폰 관리 페이지
  # 쿠폰 발행 및 관리. 쿠폰 사용 내역 확인 기능 제공
  # 쿠폰 생성 및 쿠폰 수정 가능
  # 모든 파트너 및 관리자의 쿠폰 일괄 조회
  path('supervisor/coupon', v.coupon, name='coupon'),

  # 메세지 관리 페이지
  # 관리자에게 온 메세지 확인 및 답변 기능 제공
  # 쿠폰 전달 가능. 다만 쿠폰 생성자가 아닌 경우 쿠폰 전달 불가
  # 관리자가 보낸 쪽지의 발신자는 'supervisor'로 표시. 반대도 마찬가지
  # 쪽지는 비회원(guest_id)에게도 전달 가능
  path('supervisor/message', v.message, name='message'),

  # 배너 관리 페이지
  # 광고 배너 관리 기능 제공
  # 각 배너별 정보 수정 및 확인 가능
  path('supervisor/banner', v.banner, name='banner'),

  # 레벨 관리 페이지
  # 사용자 레벨 규칙을 설정할 수 있는 기능 제공
  # 레벨 추가, 수정 가능. 삭제는 불가.
  path('supervisor/level', v.level, name='level'),

  # 설정 페이지
  # 시스템 설정 정보를 수정할 수 있는 기능 제공
  # 시스템 설정 정보 및 이용약관 본문 수정 가능.
  path('supervisor/setting', v.setting, name='setting'),

  # API
  path('api/login', a.api_login, name='account_login'),
  path('api/logout', a.api_logout, name='account_logout'),
  path('api/upload', a.api_file_upload, name='upload'),
  path('api/receive_coupon', a.api_receive_coupon, name='receive_coupon'),
  path('api/like_post', a.api_like_post, name='like_post'),
  path('api/delete_post', a.api_delete_post, name='delete_post'),
  path('api/account', a.api_account.as_view(), name='account'),
  path('api/message', a.api_message.as_view(), name='message'),
  path('api/comment', a.api_comment.as_view(), name='comment'),
  path('api/coupon', a.api_coupon.as_view(), name='coupon'),
  # data
  re_path('^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
  re_path('^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),

]
