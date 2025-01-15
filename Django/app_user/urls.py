from django.urls import path

from . import views as v

urlpatterns = [

  # views as v
  # 메인 페이지
  # 광고 베너, 사용자 활동 요약, 추천 콘텐츠 및 이벤트 정보 표시
  # 모든 여행지 게시글을 weight룰 기준으로 정렬하여 보여줌
  path('', v.index, name='index'),

  # 회원가입 페이지
  # 사용자 정보 입력 폼 제공
  # 파트너 및 여성 회원은 가입 후 관리자 승인 필요. status = pending
  path('signup', v.signup, name='signup'),

  # 계정 찾기 페이지
  # 사용자 계정 복구 센터
  # 관리자에게 쪽지 보내기 버튼으로 대체됨.
  # 별도의 계정 찾기 기능은 없음.
  path('find_account', v.find_account, name='find_account'),

  # 프로필 페이지
  # 사용자 정보 수정 및 회원 탈퇴 기능 제공
  # 사용자 프로필 정보 표시 및 수정 기능 제공.
  # 관리자의 경우, 이 페이지를 이용하여 다른 계정 정보 수정 및 조회 가능
  path('profile', v.profile, name='profile'),

  # 사용자 활동 페이지
  # 사용자 활동 내역 및 포인트 정보 제공
  # 관리자의 경우 다른 사용자의 활동 내역 조회 가능
  path('activity', v.activity, name='activity'),

  # 북마크 페이지
  # 사용자가 북마크한 콘텐츠 목록 제공
  # 일반 게시글 형태로 북마크된 게시글 목록 표시.
  # 페이지 기능은 없음. 전부 읽괄 조회
  path('bookmark', v.bookmark, name='bookmark'),

  # 제휴 문의 페이지
  # 제휴 문의 메세지 전송 폼 및 관리자 연락처 제공
  # 관리자에게 다이렉트로 메세지 전송하기 폼 제공
  path('contact', v.contact, name='contact'),

  # 이용약관 페이지
  # 서비스 이용약관 및 개인정보 처리방침 제공
  # 이용약관은 server_settings.terms에 저장된 내용을 불러옴
  path('terms', v.terms, name='terms'),

]
