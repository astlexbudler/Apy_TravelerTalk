from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.http import HttpResponse
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from datetime import datetime

def robots_txt(request):
  return HttpResponse(
'''
User-agent: *
Allow:
Disallow: /
''', content_type="text/plain")

class VirtualModel:
  def get_absolute_url(self):
    return '/'

class ServiceModel:
  def get_absolute_url(self):
    return '/service/'

class ApplifySitemapClass(Sitemap):
  changefreq = 'monthly'

  def items(self):
    return []

  def lastmod(self, obj):
    return datetime(2023, 1, 1)

  def priority(self, obj):
    return 0

urlpatterns = [
  path('admin/', admin.site.urls),
  # / 메인 페이지
  # /signup 회원가입 페이지
  # /find_account 계정 찾기 페이지
  # /profile 프로필 페이지
  # /activity 사용자 활동 페이지
  # /bookmark 북마크 페이지
  # /contact 제휴 문의 페이지
  # /terms 이용약관 페이지
  path('', include('app_user.urls')),
  path('core/', include('app_core.urls')),
  # /partner 파트너 관리 페이지
  # /partner/write_post 광고 게시글 작성 페이지
  # /partner/rewrite_post 광고 게시글 수정 페이지
  # /partner/coupon 쿠폰 관리 페이지
  path('partner/', include('app_partner.urls')),
  # /supervisor 관리자 메인 페이지
  # /supervisor/account 계정 관리 페이지
  # /supervisor/post 게시글 관리 페이지
  # /supervisor/ad_post 광고 게시글 관리 페이지
  # /supervisor/coupon 쿠폰 관리 페이지
  # /supervisor/message 메세지 관리 페이지
  # /supervisor/write_message 메세지 작성 페이지
  # /supervisor/read_message 메세지 읽기 페이지
  # /supervisor/banner 배너 관리 페이지
  # /supervisor/level 레벨 관리 페이지
  # /supervisor/setting 설정 페이지
  path('supervisor/', include('app_supervisor.urls')),
  # /post 표준 게시판 페이지
  # /post/write_post 표준 게시글 작성 페이지
  # /post/rewrite_post 표준 게시글 수정 페이지
  # /post/post_view 표준 게시글 상세 페이지
  # /post/notice 공지사항 페이지
  # /post/event 이벤트 게시판 페이지
  # /post/write_event 이벤트 게시글 작성 페이지
  # /post/rewrite_event 이벤트 게시글 수정 페이지
  # /post/event_view 이벤트 게시글 상세 페이지
  # /post/attendance 출석 게시판 페이지
  # /post/greeting 가입인사 게시판 페이지
  # /post/review 리뷰 게시판 페이지
  # /post/write_review 리뷰 게시글 작성 페이지
  # /post/rewrite_review 리뷰 게시글 수정 페이지
  # /post/review_view 리뷰 게시글 상세 페이지
  # /post/travel 광고 게시판 페이지
  # /post/travel_view 광고 게시글 상세 페이지
  path('post/', include('app_post.urls')),
  # /coupon 쿠폰 목록 페이지(사용자)
  path('coupon/', include('app_coupon.urls')),
  # /message 메세지 목록 페이지(사용자 및 파트너)
  # /message/write 메세지 작성 페이지(사용자 및 파트너)
  # /message/read 메세지 읽기 페이지(사용자 및 파트너)
  path('message/', include('app_message.urls')),
  # apis
  # /login 로그인 API
  # /logout 로그아웃 API
  # /upload 파일 업로드 API
  # /check_id 아이디 중복 확인 API
  # /check_nickname 닉네임 중복 확인 API
  # /search_user 사용자 검색 API(닉네임 또는 아이디)
  # /send_message 메세지 발송 API
  # /read_message 메세지 읽기 API
  # /edit_user 사용자 정보 수정 API
  # /delete_user 사용자 정보 삭제 API
  # /search_coupon 쿠폰 검색 API
  # /toggle_bookmark 북마크 토글 API
  path('api/', include('app_api.urls')),
  re_path('^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
  re_path('^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
  path('favicon.ico', serve, {'document_root': settings.STATIC_ROOT, 'path': 'travelertalk/img/favicon.png'}),
  path('robots.txt', robots_txt, name='robots_txt'),
  path('sitemap.xml', sitemap, {'sitemaps': {'applify_sitemap': ApplifySitemapClass}}, name='django.contrib.sitemaps.views.sitemap'),
]
