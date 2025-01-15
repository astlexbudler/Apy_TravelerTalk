import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, get_user_model

from app_core import models as core_mo
from app_user import models as user_mo
from app_partner import models as partner_mo
from app_supervisor import models as supervisor_mo
from app_post import models as post_mo
from app_message import models as message_mo
from app_coupon import models as coupon_mo

from app_post import daos as post_do
from app_core import daos as core_do
from app_user import daos as user_do
from app_message import daos as message_do
from app_coupon import daos as coupon_do
from app_partner import daos as partner_do

# 기본 컨텍스트
# server, account, messages, boards
def get_default_context(request):

  # 사용자 프로필 정보 가져오기
  # 로그인하지 않은 사용자는 guest로 처리
  account = user_do.get_user_profile(request)

  # 읽지 않는 쪽지 미리보기
  # 관리자의 경우 수신자가 'supervisor'인 쪽지로 검색해서 가져옴
  messages = message_do.get_user_message_previews(request)

  # 서버 설정 가져오기
  server = core_do.get_server_settings()

  # 게시판 트리 가져오기
  # 게시판 트리는 최대 4단계까지 구성됨.
  boards = post_do.get_boards()

  return {
    'server': server,
    'account': account,
    'messages': messages,
    'boards': boards,
  }

# 쿠폰 조회 페이지(사용자 및 여성회원 전용)
def index(request):
  context = get_default_context(request)
  if context['account']['account_type'] == 'partner':
    return redirect('/partner/coupon')
  elif 'supervisor' in context['account']['account_type']:
    return redirect('/supervisor/coupon')
  elif context['account']['account_type'] == 'guest':
    return redirect('/?redirect=need_login')

  # data
  tab = request.GET.get('tab', 'coupon')
  page = int(request.GET.get('page', '1'))

  # search
  if tab == 'coupon': # 쿠폰 검색 탭
    cps = coupon_mo.COUPON.objects.filter(
      own_user_id=context['account']['id']
    ).order_by('-created_dt')
    last_page = int(len(cps) / 20) + 1 # 한 페이지당 20개씩 표시
    coupons = []
    for cpn in cps[20 * (page - 1):20 * page]:

      # 쿠폰 관련 게시글 및 생성자 정보
      cp_post = post_mo.POST.objects.filter(id=cpn.post_id).first()
      cp_create_account = core_mo.CustomUser.objects.filter(username=cpn.create_account_id).first()
      if cp_post and cp_create_account: # 게시글 및 생성자 정보가 존재할 경우에만 추가
        coupons.append({
          'id': cpn.id,
          'code': cpn.code,
          'name': cpn.name,
          'create_account': { # 쿠폰 생성자 정보
            'id': cpn.create_account_id,
            'nickname': cp_create_account.first_name,
          },
          'description': cpn.description,
          'images': cpn.images.split(','), # 쿠폰 이미지는 하나씩만 있음...
          'post': { # 쿠폰 관련 게시글
            'id': cpn.post_id,
            'title': cp_post.title,
          },
          'created_dt': cpn.created_dt,
          'required_point': cpn.required_point,
        })

    return render(request, 'coupon/index.html', {
      **context,
      'profile': user_do.get_user_profile(request),
      'own_coupons': coupons,
      'last_page': last_page, # page 처리 작업에 사용(반드시 필요)
    })
  else: # 쿠폰 사용 내역 기록 조회 탭
    chs = coupon_mo.COUPON_HISTORY.objects.filter(
      used_user_id=context['account']['id']
    ).order_by('-created_dt')
    last_page = int(len(chs) / 20) + 1 # 한 페이지당 20개씩 표시
    coupon_histories = []
    for ch in chs[20 * (page - 1):20 * page]:

      # 쿠폰 관련 게시글 및 생성자 정보
      ch_post = post_mo.POST.objects.filter(id=ch.post_id).first()
      ch_create_account = core_mo.CustomUser.objects.filter(username=ch.create_account_id).first()
      if ch_post and ch_create_account: # 게시글 및 생성자 정보가 존재할 경우에만 추가
        coupon_histories.append({
          'id': ch.id,
          'code': ch.code,
          'name': ch.name,
          'create_account': { # 쿠폰 생성자 정보
            'id': ch.create_account_id,
            'nickname': ch_create_account.first_name,
          },
          'description': ch.description,
          'images': ch.images.split(','), # 쿠폰 이미지는 하나씩만 있음...
          'post': { # 쿠폰 관련 게시글
            'id': ch.post_id,
            'title': ch_post.title,
          },
          'created_dt': ch.created_dt,
          'used_dt': ch.used_dt,
          'status': ch.status,
        })

    return render(request, 'coupon/index.html', {
      **context,
      'profile': user_do.get_user_profile(request),
      'coupon_histories': coupon_histories,
      'last_page': last_page, # page 처리 작업에 사용(반드시 필요)
    })