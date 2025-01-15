import datetime
import random
import string
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, logout, get_user_model
from django.db.models import Q

from app_core import models as core_mo
from app_user import models as user_mo
from app_partner import models as partner_mo
from app_supervisor import models as supervisor_mo
from app_post import models as post_mo
from app_message import models as message_mo
from app_coupon import models as coupon_mo

from app_core import daos as core_do
from app_user import daos as user_do
from app_post import daos as post_do

def get_user_profile(request):

  # 기본 프로필 정보(비회원)
  # 비회원은 게스트 키가 생성되어 세션에 저장됨
  # 게스트키는 비회원 메세지를 발송하고 확인하는데 사용됨.
  guest_id = request.session['guest_id'] if 'guest_id' in request.session else None
  if not guest_id:
    guest_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
  request.session['guest_id'] = guest_id
  account = {
    'id': guest_id,
    'nickname': '게스트',
    'account_type': 'guest',
    'status': 'active',
    'bookmarks': []
  }

  # 사용자 로그인 및 활성 상태 확인
  if request.user.is_authenticated:
    if request.user.status == 'active' or request.user.status == 'pending':

      # 사용자 프로필 정보
      account = {
      'id': request.user.username,
      'nickname': request.user.first_name,
      'account_type': request.user.account_type,
      'status': request.user.status,
      'bookmarks': post_do.get_user_bookmarks(request.user),
      'bookmark_ids': request.user.user_bookmarks,
      'user_usable_point': request.user.user_usable_point if request.user.account_type == 'user' or request.user.account_type == 'dame' else None,
      'user_level_point': request.user.user_level_point if request.user.account_type == 'user' or request.user.account_type == 'dame' else None,
      'user_level': core_do.get_user_level(request.user) if request.user.account_type == 'user' or request.user.account_type == 'dame' else None,
      'partner_tel': request.user.partner_tel if request.user.account_type == 'partner' else None,
      'partner_address': request.user.partner_address if request.user.account_type == 'partner' else None,
      'partner_categories': request.user.partner_categories if request.user.account_type == 'partner' else None,
      'supervisor_permissions': request.user.supervisor_permissions if request.user.account_type == 'supervisor' else None
    }

  return account

def get_user_profile_by_id(user_id):
  account = {
    'id': user_id,
    'nickname': '게스트',
    'account_type': 'guest',
    'status': 'active',
    'bookmarks': []
  }

  # 사용자 로그인 및 활성 상태 확인
  user = get_user_model().objects.get(username=user_id)
  if user.status == 'active' or user.status == 'pending':

    # 사용자 프로필 정보
    account = {
      'id': user.username,
      'nickname': user.first_name,
      'account_type': user.account_type,
      'status': user.status,
      'bookmarks': post_do.get_user_bookmarks(user),
      'user_usable_point': user.user_usable_point if user.account_type == 'user' or user.account_type == 'dame' else None,
      'user_level_point': user.user_level_point if user.account_type == 'user' or user.account_type == 'dame' else None,
      'user_level': core_do.get_user_level(user) if user.account_type == 'user' or user.account_type == 'dame' else None,
      'partner_tel': user.partner_tel if user.account_type == 'partner' else None,
      'partner_address': user.partner_address if user.account_type == 'partner' else None,
      'partner_categories': user.partner_categories if user.account_type == 'partner' else None,
      'supervisor_permissions': user.supervisor_permissions if 'supervisor' in user.account_type else None,
      'note': user.note
    }

  return account

# 사용자(user, dame, partner))의 활동 기록을 가져옴.
def get_user_activities(user, page):
  activities = []

  # 사용자 로그인 여부 또는 상태와 관계없이 활동 기록을 가져옴.
  acts = user_mo.ACTIVITY.objects.filter(
    Q(user_id=user)
  ).order_by('-created_dt')
  last_page = acts.count() // 20 + 1 # 한 페이지당 20개씩 조회
  for act in acts[(page-1)*20:page*20]:
    activities.append({
      'id': act.id,
      'location': act.location,
      'message': act.message,
      'point_change': act.point_change,
      'created_dt': act.created_dt,
    })

  return {
    'activities': activities,
    'last_page': last_page,
  }

def get_account_activitie_preview(account):
  activities = []

  # 사용자 타입이 user, dame, partner인 경우에만 활동 기록을 가져옴.
  # (guest, supervisor는 활동 기록을 조회 x)
  if any(account['account_type'] in s for s in ['user', 'dame', 'partner']):
    acts = user_mo.ACTIVITY.objects.filter( # preview는 최근 5개만 조회
      Q(user_id=account['id'])
    ).order_by('-created_dt')[:5]
    for act in acts:

      # 활동 기록을 리스트에 추가
      # location은 preview에서는 가져오기 않움
      activities.append({
        'id': act.id,
        'message': act.message,
        'point_change': act.point_change,
        'created_dt': act.created_dt,
      })

  return activities