import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, get_user_model

from app_core import models
from app_core import daos

# 쿠폰 조회 페이지(사용자 및 여성회원 전용)
def index(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree() # 게시판 정보 가져오기

  # 로그인 여부 확인
  if not request.user.is_authenticated: # 로그인이 되어 있지 않은 경우
    return redirect('/?redirect_message=need_login') # 로그인 페이지로 리다이렉트

  # 파트너 또는 관리자의 경우, 리다이렉트
  if 'partner' in contexts['account']['groups']: # 파트너인 경우
    return redirect('/partner/coupon') # 파트너 쿠폰 페이지로 리다이렉트
  elif 'supervisor' in contexts['account']['groups'] or 'sub_supervisor' in contexts['account']['groups']: # 관리자인 경우
    return redirect('/supervisor/coupon') # 관리자 쿠폰 페이지로 리다이렉트

  # 데이터 가져오기
  tab = request.GET.get('tab', 'coupon') # coupon 또는 history
  page = int(request.GET.get('page', '1'))

  # 사용자 프로필
  profile = daos.get_user_profile_by_id(request)

  if tab == 'coupon': # 사용 가능한 쿠폰 정보 가져오기
    coupons, last_page = daos.get_all_user_coupons(contexts['account']['id'], page)
  elif tab == 'history': # 사용했거나 만료된 쿠폰 정보 가져오기
    coupons, last_page = daos.get_all_coupon_histories(contexts['account']['id'], page)

  return render(request, 'coupon/index.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'profile': profile, # 사용자 프로필 정보
    'coupons': coupons, # 쿠폰 정보
    'last_page': last_page, # page 처리 작업에 사용(반드시 필요)
  })