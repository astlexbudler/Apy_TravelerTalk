from django.urls import path

from . import apis as a

urlpatterns = [

  # apis as a
  # 로그인 api
  # id, password => 'success'(성공 시) or 'pending'(승인 대기중인 아이디) or 'error'(실패 시)
  path('login', a.account_login, name='account_login'),

  # 로그아웃 api
  # 로그인 세션 삭제
  path('logout', a.account_logout, name='account_logout'),

  # 파일 업로드 api
  # 파일을 업로드하고 업로드된 파일의 URL을 반환
  path('upload', a.upload, name='upload'),

  # 사용자 API
  # POST-create: 사용자 정보 생성
  # GET: 사용자 정보 검색
  # POST-update: 사용자 정보 수정
  path('account', a.account, name='account'),

  # 메세지 API
  # POST: 메세지 발송
  # GET: 메세지 읽음 처리
  path('message', a.message, name='message'),

  # 댓글 API
  # POST: 댓글 작성
  # DELETE: 댓글 삭제
  path('comment', a.comment, name='comment'),

  # 쿠폰 API
  # POST-create: 쿠폰 생성
  # GET: 쿠폰 검색
  # POST-patch: 쿠폰 수정
  path('coupon', a.coupon, name='coupon'),

  # 아이디 중복 확인 api
  # id => 'exist'(존재하는 아이디) or 'not_exist'(존재하지 않는 아이디)
  path('check_id', a.check_id, name='check_id'),

  # 닉네임 중복 확인 api
  # nickname => 'exist'(존재하는 닉네임) or 'not_exist'(존재하지 않는 닉네임)
  path('check_nickname', a.check_nickname, name='check_nickname'),

  # 쿠폰 받기 api
  path('receive_coupon', a.receive_coupon, name='receive_coupon'),

  # 게시글 좋아요 토글 api
  path('like_post', a.like_post, name='like_post'),

]
