from django.urls import path

from . import views as v

urlpatterns = [

  # views as v
  # 쿠폰 조회 페이지(사용자 및 여성회원 전용)
  # 관리자 또는 파트너 계정은 별도의 쿠폰 관리 페이지를 통해서 쿠폰을 생성 및 관리함.
  # 사용자가 보유한 쿠폰을 조회할 수 있는 페이지
  path('', v.index, name='index'),

]
