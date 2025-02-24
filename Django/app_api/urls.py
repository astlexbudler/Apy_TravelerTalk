from django.urls import path
from . import apis as a

####################
# APIS
# *데이터베이스 처리 로직은 app_core.daos.py에 구현되어있습니다. 여기서는 API 로직만 구현합니다.
# *여기서는 권한, 사용자 요청 값 확인 등의 작업만 수행합니다.
# def api_login(request): 로그인 api
# def api_logout(request): 로그아웃 api
# def api_file_upload(request): 파일 업로드 api
# def api_receive_coupon(request): 쿠폰 받기 api
# def api_like_post(request): 게시글 좋아요 토글 api
# class api_account(APIView): 사용자 REST API
# - GET: search 사용자. id, nickname, any로 검색 가능. (id, nickname, status 반환)
# - POST: create 사용자. id, password, nickname, partner_name, email(선택), account_type(user, dame, partner, subsupervisor)를 받아 사용자 생성.
# - PATCH: update 사용자. password, nickname, partner_name, email, status, note, subsupervisor_permissions를 받아 사용자 수정.
# class api_message(APIView): 메세지 REST API
# - GET: 메세지 읽음 처리. message_id를 받아 메세지의 is_read를 True로 변경.
# - POST: create 메세지. sender, receiver, title, content, image, include_coupon_code를 받아 메세지 생성.
# class api_comment(APIView): 댓글 REST API
# - POST: create 댓글. post_id, account_id, content을 받아 댓글 생성.
# - PATCH: update 댓글. comment_id, content를 받아 댓글 수정.
# - DELETE: delete 댓글. comment_id를 받아 댓글 삭제.
# class api_coupon(APIView): 쿠폰 REST API
# - GET: search 쿠폰. code를 받아 쿠폰 검색.
# - POST: create 쿠폰. code, title, content, image, expire_date, required_mileage, related_post_id를 받아 쿠폰 생성.
# - PATCH: update 쿠폰. code, title, content, image, expire_date, required_mileage, own_account_id, status를 받아 쿠폰 수정.


urlpatterns = [

  # apis as a
  # 로그인 api
  # id, password => 'success'(성공 시) or 'pending'(승인 대기중인 아이디) or 'error'(실패 시)
  path('login', a.api_login, name='account_login'),

  # 로그아웃 api
  # 로그인 세션 삭제
  path('logout', a.api_logout, name='account_logout'),

  # 파일 업로드 api
  # 파일을 업로드하고 업로드된 파일의 URL을 반환
  path('upload', a.api_file_upload, name='upload'),

  # 쿠폰 받기 api
  # 쿠폰 코드를 받아 쿠폰을 받음
  path('receive_coupon', a.api_receive_coupon, name='receive_coupon'),

  # 게시글 좋아요 토글 api
  # 게시글 id를 받아 좋아요 토글
  path('like_post', a.api_like_post, name='like_post'),

  # 사용자 API
  # POST-create: 사용자 정보 생성
  # GET: 사용자 정보 검색
  # POST-update: 사용자 정보 수정
  path('account', a.api_account.as_view(), name='account'),

  # 메세지 API
  # POST: 메세지 발송
  # GET: 메세지 읽음 처리
  path('message', a.api_message.as_view(), name='message'),

  # 댓글 API
  # POST: 댓글 작성
  # DELETE: 댓글 삭제
  path('comment', a.api_comment.as_view(), name='comment'),

  # 쿠폰 API
  # POST-create: 쿠폰 생성
  # GET: 쿠폰 검색
  # POST-patch: 쿠폰 수정
  path('coupon', a.api_coupon.as_view(), name='coupon'),

]
