from django.urls import path
from django.urls import re_path
from django.views.static import serve
from django.conf import settings
from django.urls import include

from . import views as v

urlpatterns = [

  # views as v
  # 관리자 로그인
  path('', v.login, name='login'),

  # 파트너 관리 페이지
  # 광고 게시글 작성 쿠폰 관리 메뉴 제공
  # 광고 게시글 요약 및 사용자 프로필 확인 가능
  path('partner/', v.index, name='index'),

  # 새 광고 게시글 작성 페이지
  # 이미 광고 게시글이 있는 경우, 수정 페이지로 이동
  path('partner/write_post', v.rewrite_post, name='rewrite_post'),

  # 광고 게시글 수정 페이지
  # 광고 게시글 수정 폼 제공
  path('partner/rewrite_post', v.rewrite_post, name='rewrite_post'),

  # 쿠폰 관리 페이지
  # 새 쿠폰 발급 폼 및 쿠폰 목록 제공
  # 내가 발급한 쿠폰의 사용 내역 확인 가능
  # 쿠폰 코드 검색 및 사용 처리 가능
  path('partner/coupon', v.coupon, name='coupon'),

  path('api/', include('app_api.urls')),
  re_path('^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
  re_path('^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),

]
