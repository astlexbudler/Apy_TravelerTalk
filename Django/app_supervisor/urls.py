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
  path('supervisor/supervisor', v.index, name='index'),

  # 계정 관리 페이지
  path('supervisor/account', v.account, name='account'),

  # 프로필
  path('supervisor/account/profile', v.profile, name='profile'),

  # 활동
  path('supervisor/account/activity', v.activity, name='activity'),

  # 게시글 관리 페이지
  path('supervisor/post', v.post, name='post'),

  # 게시글 수정 페이지
  path('supervisor/post/edit', v.post_edit, name='post_edit'),

  # 여행지 게시글 관리 페이지
  path('supervisor/travel', v.travel, name='travel'),

  # 여행지 게시글 수정 페이지
  path('supervisor/travel/edit', v.travel_edit, name='travel_edit'),

  # 쿠폰 관리 페이지
  path('supervisor/coupon', v.coupon, name='coupon'),

  # 메세지 관리 페이지
  path('supervisor/message', v.message, name='message'),

  # 배너 관리 페이지
  path('supervisor/banner', v.banner, name='banner'),

  # 레벨 관리 페이지
  path('supervisor/level', v.level, name='level'),

  # 설정 페이지
  path('supervisor/setting', v.setting, name='setting'),

  # API
  path('api/login', a.api_login, name='account_login'),
  path('api/logout', a.api_logout, name='account_logout'),
  path('api/upload', a.api_file_upload, name='upload'),
  path('api/post', a.api_post.as_view(), name='post'),
  path('api/account', a.api_account.as_view(), name='account'),
  path('api/message', a.api_message.as_view(), name='message'),
  path('api/comment', a.api_comment.as_view(), name='comment'),
  path('api/coupon', a.api_coupon.as_view(), name='coupon'),
  path('api/board', a.api_board.as_view(), name='board'),
  path('api/category', a.api_category.as_view(), name='category'),
  path('api/ip_block', a.api_ip_block.as_view(), name='ip_block'),
  # data
  re_path('^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
  re_path('^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),

]
