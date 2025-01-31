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

  # 회원가입 api
  # id, password, nickname, category, tel, address, account_type
  path('signup', a.signup, name='signup'),

  # 파일 업로드 api
  # 파일을 업로드하고 업로드된 파일의 URL을 반환
  path('upload', a.upload, name='upload'),

  # 아이디 중복 확인 api
  # id => 'exist'(존재하는 아이디) or 'not_exist'(존재하지 않는 아이디)
  path('check_id', a.check_id, name='check_id'),

  # 닉네임 중복 확인 api
  # nickname => 'exist'(존재하는 닉네임) or 'not_exist'(존재하지 않는 닉네임)
  path('check_nickname', a.check_nickname, name='check_nickname'),

  # 사용자 검색 api(닉네임 또는 아이디) 완전 일치 여부를 검색
  # id_or_nickname => 사용자 정보 리스트
  path('search_user', a.search_user, name='search_user'),

  # 메세지 발송 api
  # receiver_id, title, content, include_coupon, images(이미지 경로) => 'success', message_id
  path('send_message', a.send_message, name='send_message'),

  # 사용자 정보 수정
  # 수정할 사용자 정보를 전달하면 해당 값만 수정됨.
  # 관리자일 경우 사용자 아이디를 같이 전달하면 해당 사용자의 정보 수정 가능
  path('edit_user', a.edit_user, name='edit_user'),

  # 사용자 정보 삭제
  # 사용자의 status를 'deleted'로 변경(90일 후 데이터베이스에서 삭제 - scheduler로 처리)
  # 관리자의 경우 사용자 아이디를 같이 전달하면 해당 사용자의 정보 삭제 가능
  path('delete_user', a.delete_user, name='delete_user'),

  # 쿠폰 검색
  # code => 쿠폰 정보
  # 쿠폰 정보 및 관련 게시물 제목, 소유자 및 생성자 정보 반환
  path('search_coupon', a.search_coupon, name='search_coupon'),

  # 댓글 작성 api
  # post_id, target_comment_id(대댓글), content => 'success'
  path('write_comment', a.write_comment, name='write_comment'),

  # 댓글 삭제 api
  # comment_id => 'success'
  path('delete_comment', a.delete_comment, name='delete_comment'),

  # 메세지 읽음 처리 api
  path('read_message', a.read_message, name='read_message'),

  # 쿠폰 받기 api
  path('receive_coupon', a.receive_coupon, name='receive_coupon'),

  # 게시글 좋아요 토글 api
  path('like_post', a.like_post, name='like_post'),

]
