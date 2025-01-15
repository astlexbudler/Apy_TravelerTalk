from django.urls import path

from . import views as v

urlpatterns = [

  # views as v
  # 메세지 목록 페이지(사용자 및 파트너, 게스트)
  # 보낸 쪽지 및 받은 쪽지를 확인할 수 있는 페이지 제공(?tab= 으로 구분)
  # 쪽지 확인 및 보내기 모달 포함
  # 쪽지에 쿠폰이 포함되어 있는 경우 쿠폰을 받을 수 있음(사용자의 경우)
  # 파트너 또는 관리자의 경우. 쪽지에 쿠폰을 담아서 사용자에게 보낼 수 있음. => 다만 관리자는 /supervisor/message 페이지를 이용함.
  path('', v.index, name='index'),

  # 메세지 작성 페이지(사용자 및 파트너)
  # 사용자가 다른 사용자 또는 관리자에게 메세지를 작성할 수 있는 폼 제공
  #path('write', v.write, name='write'), => 모달로 대체됨

  # 메세지 읽기 페이지(사용자 및 파트너)
  # 사용자가 받은 메세지의 내용을 확인할 수 있는 페이지 제공
  # path('read', v.read, name='read'), => 모달로 대체됨

]
