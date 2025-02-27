import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, get_user_model
from django.conf import settings

from app_core import models
from app_core import daos

# 쿠폰 조회 페이지(사용자 및 여성회원 전용)
def index(request):
  # account, activities(5), unread_messages(5), coupons(5), server, best_reviews(5)
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree(contexts['account']['account_type']) # 게시판 정보

  # 로그인 여부 확인
  if contexts['account']['account_type'] == 'guest': # 비회원인 경우
    return redirect('/?redirect_message=need_login') # 로그인 페이지로 리다이렉트

  # 파트너 또는 관리자의 경우, 리다이렉트
  if contexts['account']['account_type'] in ['partner']: # 파트너인 경우
    return redirect(settings.PARTNER_URL + '/partner/coupon') # 파트너 쿠폰 페이지로 리다이렉트
  elif contexts['account']['account_type'] in ['supervisor', 'subsupervisor']: # 관리자인 경우
    return redirect(settings.SUPERVISOR_URL + '/supervisor/coupon') # 관리자 쿠폰 페이지로 리다이렉트

  # 데이터 가져오기
  tab = request.GET.get('tab', 'coupon') # coupon 또는 history
  page = int(request.GET.get('page', '1')) # 페이지 번호

  if tab == 'couponTab': # 사용 가능한 쿠폰 정보 가져오기
    coupons, last_page = daos.select_owned_coupons(status='active', account_id=contexts['account']['id'], page=page)
  else: # 사용했거나 만료된 쿠폰 정보 가져오기
    coupons, last_page = daos.select_owned_coupons(status='used', account_id=contexts['account']['id'], page=page)

  return render(request, 'coupon/coupon.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'coupons': coupons, # 쿠폰 정보
    'last_page': last_page, # page 처리 작업에 사용(반드시 필요)
  })