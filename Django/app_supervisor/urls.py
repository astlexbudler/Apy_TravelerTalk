from django.urls import path

from . import views as v

urlpatterns = [

  # views as v
  # 관리자 메인 페이지
  # 계정 관리, 게시글 관리, 쿠폰 관리, 메세지 관리, 배너 관리, 설정 메뉴 제공
  # TODO: 현재 해당 페이지에 아무것도 없음. 추후 추가 예정. 디자인 담당자 확인 필요
  path('', v.index, name='index'),

  # 계정 관리 페이지
  # 사용자 계정 종류 별 계정 정보 제공. 비밀번호 초기화 및 계정 삭제 기능 제공
  # account_type 별로 별도의 탭 제공.
  # 관리자 아이디 생성 기능 제공(최상위 관리자만 관리자 아이디 생성 가눙)
  # 사용자 정보 수정 기능 제공(사용자 비밀번호 덮어쓰기 기능 제공)
  path('account', v.account, name='account'),

  # 게시글 관리 페이지
  # 게시글 목록 및 게시글 삭제 기능 제공
  # 게시글 수정 페이지로 이동 가능
  # 간단하게 게시글 정보 조회
  path('post', v.post, name='post'),

  # 광고 게시글 관리 페이지
  # 광고 게시글 관리 기능 제공
  # 광고 게시글 == 여행지 정보 게시글
  # 각 광고 게시글 별 광고 정책 확인 가능
  # 광고 정책 수정 기능 제공
  path('ad_post', v.ad_post, name='ad_post'),

  # 쿠폰 관리 페이지
  # 쿠폰 발행 및 관리. 쿠폰 사용 내역 확인 기능 제공\
  # 쿠폰 생성 및 쿠폰 수정 가능
  # 모든 파트너 및 관리자의 쿠폰 일괄 조회
  path('coupon', v.coupon, name='coupon'),

  # 메세지 관리 페이지
  # 관리자에게 온 메세지 확인 및 답변 기능 제공
  # 쿠폰 전달 가능. 다만 쿠폰 생성자가 아닌 경우 쿠폰 전달 불가
  # 관리자가 보낸 쪽지의 발신자는 'supervisor'로 표시. 반대도 마찬가지
  # 쪽지는 비회원(guest_id)에게도 전달 가능
  path('message', v.message, name='message'),

  # 메세지 작성 페이지
  # 관리자가 사용자에게 메세지를 작성할 수 있는 기능 제공
  #path('write_message', v.write_message, name='write_message'),

  # 메세지 읽기 페이지
  # 사용자가 보낸 메세지 내용을 확인할 수 있는 기능 제공
  #path('read_message', v.read_message, name='read_message'),

  # 배너 관리 페이지
  # 광고 배너 관리 기능 제공
  # 각 배너별 정보 수정 및 확인 가능
  path('banner', v.banner, name='banner'),

  # 레벨 관리 페이지
  # 사용자 레벨 규칙을 설정할 수 있는 기능 제공
  # 레벨 추가, 수정 가능. 삭제는 불가.
  path('level', v.level, name='level'),

  # 설정 페이지
  # 시스템 설정 정보를 수정할 수 있는 기능 제공
  # 시스템 설정 정보 및 이용약관 본문 수정 가능.
  path('setting', v.setting, name='setting'),

]
