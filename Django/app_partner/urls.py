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

  # 파트너 관리 페이지
  path('partner/partner', v.index, name='index'),

  # 새 광고 게시글 작성 페이지
  path('partner/write_post', v.write_post, name='write_post'),

  # 광고 게시글 수정 페이지
  path('partner/rewrite_post', v.rewrite_post, name='rewrite_post'),

  # 쿠폰
  path('partner/coupon', v.coupon, name='coupon'),

  # 프로필
  path('partner/profile', v.profile, name='profile'),
  path('partner/activity', v.activity, name='activity'),

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
