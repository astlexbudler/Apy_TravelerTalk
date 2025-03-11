from django.urls import path
from . import apis as a

urlpatterns = [

  # apis as a
  # 로그인 api
  path('login', a.api_login, name='account_login'),

  # 로그아웃 api
  path('logout', a.api_logout, name='account_logout'),

  # 파일 업로드 api
  path('upload', a.api_file_upload, name='upload'),

  # 쿠폰 게시글에서 쿠폰 수령 api
  path('coupon_receive', a.api_coupon_receive, name='coupon_receive'),

  # 게시글 API
  # GET: 게시글 조회
  # DELETE: 게시글 삭제
  # PATCH: 게시글 좋아요 토글
  path('post', a.api_post.as_view(), name='post'),

  # 사용자 API
  # POST: 사용자 정보 생성
  # GET: 사용자 정보 검색
  # PATCH: 사용자 정보 수정
  path('account', a.api_account.as_view(), name='account'),

  # 메세지 API
  # POST: 메세지 발송
  # GET: 메세지 읽음 처리 및 쿠폰 수령
  path('message', a.api_message.as_view(), name='message'),

  # 댓글 API
  # POST: 댓글 작성
  # PATCH: 댓글 수정
  # DELETE: 댓글 삭제
  path('comment', a.api_comment.as_view(), name='comment'),

  # 쿠폰 API
  # POST: 쿠폰 생성
  # GET: 쿠폰 검색
  # PATCH: 쿠폰 수정
  path('coupon', a.api_coupon.as_view(), name='coupon'),

  # 게시판 API
  # POST: 게시판 생성
  # PATCH: 게시판 수정
  # DELETE: 게시판 삭제
  path('board', a.api_board.as_view(), name='board'),

  # 카테고리 API
  # POST: 카테고리 생성
  # PATCH: 카테고리 수정
  # DELETE: 카테고리 삭제
  path('category', a.api_category.as_view(), name='category'),

  # IP 차단 API
  # POST: IP 차단
  # DELETE: IP 차단 해제
  path('ip_block', a.api_ip_block.as_view(), name='ip_block'),

]
