import datetime
import math
import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, get_user_model
from django.db.models import Q, Count, Case, When, Value, IntegerField
from django.contrib.auth.models import Group
from django.conf import settings

from app_core import models
from app_core import daos

# 관리자 로그인
def login(request):

  # 권한 확인
  if request.user.is_authenticated:
    account = daos.select_account_detail(request.user.id)
  else:
    return render(request, 'login.html')
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return render(request, 'login.html')

  return redirect(settings.SUPERVISOR_URL + '/supervisor/supervisor')

# 관리자 메인 페이지
def index(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)

  # 파트너 가입 및 파트너 가입 대기중인 사용자 수
  all_partner = models.ACCOUNT.objects.prefetch_related('groups').filter(
    Q(groups__name='partner')
  )
  active_partner = all_partner.filter(status='active').count()
  pending_partner = all_partner.filter(status='pending').count()

  # qna 게시판에 개시글 중 댓글이 없는 게시글과 있는 게시글 수
  all_qna = models.POST.objects.prefetch_related('boards').filter(
    Q(boards__board_type='qna')
  )
  qna_no_answer = 0
  qna_answer = 0
  for qna in all_qna:
    comment_count = models.COMMENT.objects.filter(post=qna).count()
    if comment_count == 0:
      qna_no_answer += 1
    else:
      qna_answer += 1

  # 사용 가능한 쿠폰 갯수와 사용된 쿠폰 갯수. 관리자에게 도착한 쿠폰 요청 메세지 갯수
  active_coupon_count = models.COUPON.objects.filter(
    status='active'
  ).count()
  used_coupon_count = models.COUPON.objects.filter(
    ~Q(status='active')
  ).count()
  coupon_request_message_count = models.MESSAGE.objects.filter(
    message_type='coupon_request',
    is_read=False,
    receive__isnull=True
  ).count()

  # 여행지 게시글 광고 정보
  place_on_ad_count = models.PLACE_INFO.objects.filter(
    status='ad',
  ).count()
  place_on_ad_count += models.PLACE_INFO.objects.select_related(
    'post'
  ).filter(
    status='active',
    post__search_weight__gt=0
  ).count()
  place_ad_request_count = models.MESSAGE.objects.filter(
    message_type='ad_request',
    is_read=False,
    receive__isnull=True
  ).count()

  # 통계 데이터 가져오기
  today = datetime.datetime.now()
  ago_7day = today - datetime.timedelta(days=7)
  ago_6day = today - datetime.timedelta(days=6)
  ago_5day = today - datetime.timedelta(days=5)
  ago_4day = today - datetime.timedelta(days=4)
  ago_3day = today - datetime.timedelta(days=3)
  ago_2day = today - datetime.timedelta(days=2)
  ago_1day = today - datetime.timedelta(days=1)

  # 쿠폰 생성 건수
  coupon_create_7_to_6 = models.STATISTIC.objects.filter(
    name='coupon_create',
    date=ago_7day
  ).first()
  if not coupon_create_7_to_6:
    coupon_create_7_to_6 = 0
  else:
    coupon_create_7_to_6 = coupon_create_7_to_6.value
  coupon_create_6_to_5 = models.STATISTIC.objects.filter(
    name='coupon_create',
    date=ago_6day
  ).first()
  if not coupon_create_6_to_5:
    coupon_create_6_to_5 = 0
  else:
    coupon_create_6_to_5 = coupon_create_6_to_5.value
  coupon_create_5_to_4 = models.STATISTIC.objects.filter(
    name='coupon_create',
    date=ago_5day
  ).first()
  if not coupon_create_5_to_4:
    coupon_create_5_to_4 = 0
  else:
    coupon_create_5_to_4 = coupon_create_5_to_4.value
  coupon_create_4_to_3 = models.STATISTIC.objects.filter(
    name='coupon_create',
    date=ago_4day
  ).first()
  if not coupon_create_4_to_3:
    coupon_create_4_to_3 = 0
  else:
    coupon_create_4_to_3 = coupon_create_4_to_3.value
  coupon_create_3_to_2 = models.STATISTIC.objects.filter(
    name='coupon_create',
    date=ago_3day
  ).first()
  if not coupon_create_3_to_2:
    coupon_create_3_to_2 = 0
  else:
    coupon_create_3_to_2 = coupon_create_3_to_2.value
  coupon_create_2_to_1 = models.STATISTIC.objects.filter(
    name='coupon_create',
    date=ago_2day
  ).first()
  if not coupon_create_2_to_1:
    coupon_create_2_to_1 = 0
  else:
    coupon_create_2_to_1 = coupon_create_2_to_1.value
  coupon_create_1_to_0 = models.STATISTIC.objects.filter(
    name='coupon_create',
    date=ago_1day
  ).first()
  if not coupon_create_1_to_0:
    coupon_create_1_to_0 = 0
  else:
    coupon_create_1_to_0 = coupon_create_1_to_0.value

  # 쿠폰 사용 건수
  coupon_use_7_to_6 = models.STATISTIC.objects.filter(
    name='coupon_use',
    date=ago_7day
  ).first()
  if not coupon_use_7_to_6:
    coupon_use_7_to_6 = 0
  else:
    coupon_use_7_to_6 = coupon_use_7_to_6.value
  coupon_use_6_to_5 = models.STATISTIC.objects.filter(
    name='coupon_use',
    date=ago_6day
  ).first()
  if not coupon_use_6_to_5:
    coupon_use_6_to_5 = 0
  else:
    coupon_use_6_to_5 = coupon_use_6_to_5.value
  coupon_use_5_to_4 = models.STATISTIC.objects.filter(
    name='coupon_use',
    date=ago_5day
  ).first()
  if not coupon_use_5_to_4:
    coupon_use_5_to_4 = 0
  else:
    coupon_use_5_to_4 = coupon_use_5_to_4.value
  coupon_use_4_to_3 = models.STATISTIC.objects.filter(
    name='coupon_use',
    date=ago_4day
  ).first()
  if not coupon_use_4_to_3:
    coupon_use_4_to_3 = 0
  else:
    coupon_use_4_to_3 = coupon_use_4_to_3.value
  coupon_use_3_to_2 = models.STATISTIC.objects.filter(
    name='coupon_use',
    date=ago_3day
  ).first()
  if not coupon_use_3_to_2:
    coupon_use_3_to_2 = 0
  else:
    coupon_use_3_to_2 = coupon_use_3_to_2.value
  coupon_use_2_to_1 = models.STATISTIC.objects.filter(
    name='coupon_use',
    date=ago_2day
  ).first()
  if not coupon_use_2_to_1:
    coupon_use_2_to_1 = 0
  else:
    coupon_use_2_to_1 = coupon_use_2_to_1.value
  coupon_use_1_to_0 = models.STATISTIC.objects.filter(
    name='coupon_use',
    date=ago_1day
  ).first()
  if not coupon_use_1_to_0:
    coupon_use_1_to_0 = 0
  else:
    coupon_use_1_to_0 = coupon_use_1_to_0.value

  # 마일리지 사용 총합
  mileage_use_7_to_6 = models.STATISTIC.objects.filter(
    name='mileage_use',
    date=ago_7day
  ).first()
  if not mileage_use_7_to_6:
    mileage_use_7_to_6 = 0
  else:
    mileage_use_7_to_6 = mileage_use_7_to_6.value
  mileage_use_6_to_5 = models.STATISTIC.objects.filter(
    name='mileage_use',
    date=ago_6day
  ).first()
  if not mileage_use_6_to_5:
    mileage_use_6_to_5 = 0
  else:
    mileage_use_6_to_5 = mileage_use_6_to_5.value
  mileage_use_5_to_4 = models.STATISTIC.objects.filter(
    name='mileage_use',
    date=ago_5day
  ).first()
  if not mileage_use_5_to_4:
    mileage_use_5_to_4 = 0
  else:
    mileage_use_5_to_4 = mileage_use_5_to_4.value
  mileage_use_4_to_3 = models.STATISTIC.objects.filter(
    name='mileage_use',
    date=ago_4day
  ).first()
  if not mileage_use_4_to_3:
    mileage_use_4_to_3 = 0
  else:
    mileage_use_4_to_3 = mileage_use_4_to_3.value
  mileage_use_3_to_2 = models.STATISTIC.objects.filter(
    name='mileage_use',
    date=ago_3day
  ).first()
  if not mileage_use_3_to_2:
    mileage_use_3_to_2 = 0
  else:
    mileage_use_3_to_2 = mileage_use_3_to_2.value
  mileage_use_2_to_1 = models.STATISTIC.objects.filter(
    name='mileage_use',
    date=ago_2day
  ).first()
  if not mileage_use_2_to_1:
    mileage_use_2_to_1 = 0
  else:
    mileage_use_2_to_1 = mileage_use_2_to_1.value
  mileage_use_1_to_0 = models.STATISTIC.objects.filter(
    name='mileage_use',
    date=ago_1day
  ).first()
  if not mileage_use_1_to_0:
    mileage_use_1_to_0 = 0
  else:
    mileage_use_1_to_0 = mileage_use_1_to_0.value

  # 광고 신청 건수
  ad_request_7_to_6 = models.STATISTIC.objects.filter(
    name='place_ad_request',
    date=ago_7day
  ).first()
  if not ad_request_7_to_6:
    ad_request_7_to_6 = 0
  else:
    ad_request_7_to_6 = ad_request_7_to_6.value
  ad_request_6_to_5 = models.STATISTIC.objects.filter(
    name='place_ad_request',
    date=ago_6day
  ).first()
  if not ad_request_6_to_5:
    ad_request_6_to_5 = 0
  else:
    ad_request_6_to_5 = ad_request_6_to_5.value
  ad_request_5_to_4 = models.STATISTIC.objects.filter(
    name='place_ad_request',
    date=ago_5day
  ).first()
  if not ad_request_5_to_4:
    ad_request_5_to_4 = 0
  else:
    ad_request_5_to_4 = ad_request_5_to_4.value
  ad_request_4_to_3 = models.STATISTIC.objects.filter(
    name='place_ad_request',
    date=ago_4day
  ).first()
  if not ad_request_4_to_3:
    ad_request_4_to_3 = 0
  else:
    ad_request_4_to_3 = ad_request_4_to_3.value
  ad_request_3_to_2 = models.STATISTIC.objects.filter(
    name='place_ad_request',
    date=ago_3day
  ).first()
  if not ad_request_3_to_2:
    ad_request_3_to_2 = 0
  else:
    ad_request_3_to_2 = ad_request_3_to_2.value
  ad_request_2_to_1 = models.STATISTIC.objects.filter(
    name='place_ad_request',
    date=ago_2day
  ).first()
  if not ad_request_2_to_1:
    ad_request_2_to_1 = 0
  else:
    ad_request_2_to_1 = ad_request_2_to_1.value
  ad_request_1_to_0 = models.PLACE_INFO.objects.filter(
    status='pending'
  ).count()
  if not ad_request_1_to_0:
    ad_request_1_to_0 = 0
  else:
    ad_request_1_to_0 = ad_request_1_to_0

  # 광고 집행 건수
  ad_execute_7_to_6 = models.STATISTIC.objects.filter(
    name='place_on_ad',
    date=ago_7day
  ).first()
  if not ad_execute_7_to_6:
    ad_execute_7_to_6 = 0
  else:
    ad_execute_7_to_6 = ad_execute_7_to_6.value
  ad_execute_6_to_5 = models.STATISTIC.objects.filter(
    name='place_on_ad',
    date=ago_6day
  ).first()
  if not ad_execute_6_to_5:
    ad_execute_6_to_5 = 0
  else:
    ad_execute_6_to_5 = ad_execute_6_to_5.value
  ad_execute_5_to_4 = models.STATISTIC.objects.filter(
    name='place_on_ad',
    date=ago_5day
  ).first()
  if not ad_execute_5_to_4:
    ad_execute_5_to_4 = 0
  else:
    ad_execute_5_to_4 = ad_execute_5_to_4.value
  ad_execute_4_to_3 = models.STATISTIC.objects.filter(
    name='place_on_ad',
    date=ago_4day
  ).first()
  if not ad_execute_4_to_3:
    ad_execute_4_to_3 = 0
  else:
    ad_execute_4_to_3 = ad_execute_4_to_3.value
  ad_execute_3_to_2 = models.STATISTIC.objects.filter(
    name='place_on_ad',
    date=ago_3day
  ).first()
  if not ad_execute_3_to_2:
    ad_execute_3_to_2 = 0
  else:
    ad_execute_3_to_2 = ad_execute_3_to_2.value
  ad_execute_2_to_1 = models.STATISTIC.objects.filter(
    name='place_on_ad',
    date=ago_2day
  ).first()
  if not ad_execute_2_to_1:
    ad_execute_2_to_1 = 0
  else:
    ad_execute_2_to_1 = ad_execute_2_to_1.value
  ad_execute_1_to_0 = models.PLACE_INFO.objects.filter(
    status='ad',
  ).count()
  if not ad_execute_1_to_0:
    ad_execute_1_to_0 = 0
  else:
    ad_execute_1_to_0 = ad_execute_1_to_0

  # 시간
  ago_7day = ago_7day.strftime('%Y-%m-%d')
  ago_6day = ago_6day.strftime('%Y-%m-%d')
  ago_5day = ago_5day.strftime('%Y-%m-%d')
  ago_4day = ago_4day.strftime('%Y-%m-%d')
  ago_3day = ago_3day.strftime('%Y-%m-%d')
  ago_2day = ago_2day.strftime('%Y-%m-%d')
  ago_1day = ago_1day.strftime('%Y-%m-%d')
  today = today.strftime('%Y-%m-%d')

  # export
  if request.GET.get('export'):
    headers = ['', ago_6day, ago_5day, ago_4day, ago_3day, ago_2day, ago_1day, today]
    values = [
      ['coupon_create', 'coupon_use', 'mileage_use', 'ad_request', 'ad_excute'],
      [coupon_create_7_to_6, mileage_use_7_to_6, ad_request_7_to_6, ad_execute_7_to_6],
      [coupon_create_6_to_5, mileage_use_6_to_5, ad_request_6_to_5, ad_execute_6_to_5],
      [coupon_create_5_to_4, mileage_use_5_to_4, ad_request_5_to_4, ad_execute_5_to_4],
      [coupon_create_4_to_3, mileage_use_4_to_3, ad_request_4_to_3, ad_execute_4_to_3],
      [coupon_create_3_to_2, mileage_use_3_to_2, ad_request_3_to_2, ad_execute_3_to_2],
      [coupon_create_2_to_1, mileage_use_2_to_1, ad_request_2_to_1, ad_execute_2_to_1],
      [coupon_create_1_to_0, mileage_use_1_to_0, ad_request_1_to_0, ad_execute_1_to_0],
    ]
    table_data = list(zip(*values))
    return render(request, 'export.html', {
      **daos.get_urls(),
      'headers': headers,
      'table_data': table_data,
    })

  return render(request, 'supervisor/index.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'active_partner': active_partner, # 파트너 가입 수
    'pending_partner': pending_partner, # 파트너 가입 대기 수
    'qna_no_answer': qna_no_answer, # qna 게시판에 답변이 없는 게시글 수
    'qna_answer': qna_answer, # qna 게시판에 답변이 있는 게시글 수
    'active_coupon_count': active_coupon_count, # 사용 가능한 쿠폰 수
    'used_coupon_count': used_coupon_count, # 사용된 쿠폰 수
    'coupon_request_message_count': coupon_request_message_count, # 관리자에게 도착한 쿠폰 요청 메세지 수
    'place_on_ad_count': place_on_ad_count, # 광고 중인 여행지 수
    'place_ad_request_count': place_ad_request_count, # 관리자에게 도착한 여행지 광고 요청 메세지 수
    'stats': zip(
      [ago_7day, ago_6day, ago_5day, ago_4day, ago_3day, ago_2day, ago_1day, today],
      [
        coupon_create_7_to_6,
        coupon_create_6_to_5,
        coupon_create_5_to_4,
        coupon_create_4_to_3,
        coupon_create_3_to_2,
        coupon_create_2_to_1,
        coupon_create_1_to_0,
      ],
      [
        coupon_use_7_to_6,
        coupon_use_6_to_5,
        coupon_use_5_to_4,
        coupon_use_4_to_3,
        coupon_use_3_to_2,
        coupon_use_2_to_1,
        coupon_use_1_to_0,
      ],
      [
        mileage_use_7_to_6,
        mileage_use_6_to_5,
        mileage_use_5_to_4,
        mileage_use_4_to_3,
        mileage_use_3_to_2,
        mileage_use_2_to_1,
        mileage_use_1_to_0,
      ],
      [
        ad_request_7_to_6,
        ad_request_6_to_5,
        ad_request_5_to_4,
        ad_request_4_to_3,
        ad_request_3_to_2,
        ad_request_2_to_1,
        ad_request_1_to_0,
      ],
      [
        ad_execute_7_to_6,
        ad_execute_6_to_5,
        ad_execute_5_to_4,
        ad_execute_4_to_3,
        ad_execute_3_to_2,
        ad_execute_2_to_1,
        ad_execute_1_to_0,
      ]
    )
  })

# 계정 관리 페이지
def account(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)
  if 'user' not in account['subsupervisor_permissions']:
    return redirect(settings.SUPERVISOR_URL)

  # 데이터 가져오기
  tab = request.GET.get('tab', 'userTab') # user, dame, partner, supervisor
  page = int(request.GET.get('page', '1'))
  search_id = request.GET.get('username')
  search_nickname = request.GET.get('nickname', '')
  search_status = request.GET.get('status')
  search_ip = request.GET.get('ip')
  page_items = int(request.GET.get('page_items', '50'))

  # 계정 타입별로 계정 통계 가져오기
  query = Q()
  if tab == 'userTab':
    query = Q(groups__name='user')
  elif tab == 'dameTab':
    query = Q(groups__name='dame')
  elif tab == 'partnerTab':
    query = Q(groups__name='partner')
  elif tab == 'supervisorTab':
    query = Q(groups__name__in=['supervisor', 'subsupervisor'])
  accounts = models.ACCOUNT.objects.filter(query).order_by('-date_joined')

  # 계정 종류 별 통계
  status = {
    'active': accounts.filter(status='active').count(),
    'pending': accounts.filter(status='pending').count(),
    'deleted': accounts.filter(status='deleted').count(),
    'blocked': accounts.filter(status='blocked').count(),
  }

  # 이어서 검색 진행
  if search_id:
    query &= Q(username=search_id)
  if search_nickname:
    query &= Q(first_name=search_nickname)
  if search_status:
    query &= Q(status=search_status)
  if search_ip:
    query &= Q(recent_ip=search_ip)
  accounts = accounts.filter(query)

  # export
  if request.GET.get('export'):
    headers = ['아이디', '닉네임', '파트너이름', '이메일', '연락처', '계정 종류', '가입일', '마지막 로그인', '상태', '노트', '마일리지', '경험치', '부관리자 권한', '최근 접속 IP', '레벨']
    values = [
      [acnt.username for acnt in accounts],
      [acnt.first_name for acnt in accounts],
      [acnt.last_name for acnt in accounts],
      [acnt.email for acnt in accounts],
      [acnt.tel for acnt in accounts],
      [acnt.groups.all()[0].name for acnt in accounts],
      [datetime.datetime.strftime(acnt.date_joined, '%Y-%m-%d %H:%M') for acnt in accounts],
      [datetime.datetime.strftime(acnt.last_login, '%Y-%m-%d %H:%M') if acnt.last_login else None for acnt in accounts],
      [acnt.status for acnt in accounts],
      [str(acnt.note).replace(',', '.') for acnt in accounts],
      [acnt.mileage for acnt in accounts],
      [acnt.exp for acnt in accounts],
      [acnt.subsupervisor_permissions for acnt in accounts],
      [acnt.recent_ip for acnt in accounts],
      [acnt.level.level for acnt in accounts],
    ]
    table_data = list(zip(*values))
    return render(request, 'export.html', {
      **daos.get_urls(),
      'headers': headers,
      'table_data': table_data,
    })

  # 페이지네이션
  last_page = math.ceil(accounts.count() / page_items)
  accounts = accounts[(page - 1) * page_items:page * page_items]
  search_accounts = []
  for account in accounts:

    # 계정 정보
    search_accounts.append({
      'id': account.id,
      'username': account.username,
      'nickname': account.first_name,
      'partner_name': account.last_name,
      'email': account.email,
      'tel': account.tel,
      'account_type': account.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
      'status': account.status,
      'subsupervisor_permissions': str(account.subsupervisor_permissions).split(','),
      'level': daos.select_level(account.level.pk),
      'bookmarked_posts': [post.id for post in account.bookmarked_posts.all()],
      'exp': account.exp,
      'mileage': account.mileage,
      'note': account.note,
      'date_joined': datetime.datetime.strftime(account.date_joined, '%Y-%m-%d %H:%M'),
      'last_login': datetime.datetime.strftime(account.last_login, '%Y-%m-%d %H:%M') if account.last_login else None,
      'ip': account.recent_ip,
    })

  # 차단 IP 목록
  blocked_ips = [{
    'ip': blocked_ip.ip
  } for blocked_ip in models.BLOCKED_IP.objects.all()]

  # 게시판 및 카테고리
  boards = daos.make_board_tree(board_type='travel')
  categories = daos.make_category_tree()

  return render(request, 'supervisor/account.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'accounts': search_accounts, # 검색된 계정 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
    'status': status, # 사용자 종류(탭) 별 통계 데이터(관리자는 없음)
    'blocked_ips': blocked_ips, # 차단 IP 목록
    'travel_boards': boards, # 게시판 목록
    'categories': categories, # 카테고리 목록
  })

# 프로필
def profile(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)
  if 'user' not in account['subsupervisor_permissions']:
    return redirect(settings.SUPERVISOR_URL)

  # data
  account_id = request.GET.get('account_id', '')
  profile = daos.select_account_detail(account_id)

  return render(request, 'supervisor/profile.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'profile': profile,
  })

# 활동
def activity(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)

  # data
  page = int(request.GET.get('page', '1'))
  profile_id = request.GET.get('account_id', '')
  profile = daos.select_account_detail(profile_id)
  activities, last_page = daos.select_account_activities(profile_id, page)
  status = daos.get_account_activity_stats(profile_id)

  return render(request, 'supervisor/activity.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'profile': profile,
    'activities': activities,
    'status': status,
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
  })

# 게시글 관리 페이지
def post(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)
  if 'post' not in account['subsupervisor_permissions']:
    return redirect(settings.SUPERVISOR_URL)

  # 데이터가져오기
  page = int(request.GET.get('page', '1'))
  search_post_title = request.GET.get('post_title', '')
  search_board_id = request.GET.get('board_id', '')
  search_author = request.GET.get('author', '')
  page_items = int(request.GET.get('page_items', '50'))

  # 게시판별 통계 가져오기
  boards = daos.make_board_tree(status=True, board_type='not_travel')

  # 게시글 검색
  query = Q()
  query &= Q(place_info=None)
  query &= Q(author__isnull=False)
  if search_post_title: # 제목 또는 내용을 검색하도록 수정됨
    query &= Q(title__contains=search_post_title)
    query |= Q(content__contains=search_post_title)
  if search_author:
    query &= Q(author__username=search_author) # 작성자 아이디로 검색
    query &= Q(author__first_name=search_author) # 작성자 닉네임으로 검색
  if search_board_id:
    query &= Q(boards__id__contains=search_board_id)
  posts = models.POST.objects.select_related(
    'author', 'place_info'
  ).filter(query).order_by('-created_at')

  # export
  if request.GET.get('export'):
    headers = ['id', 'title', 'view_count', 'like_count', 'created_at', 'board', 'author_nickname', 'related_post_name']
    values = [
        [str(post.id) for post in posts],
        [post.title for post in posts],
        [str(post.view_count) for post in posts],
        [str(post.like_count) for post in posts],
        [datetime.datetime.strftime(post.created_at, '%Y-%m-%d %H:%M') for post in posts],
        [str(post.boards.all().last().name) for post in posts],
        [str(post.author.first_name) for post in posts],
        [str(post.related_post.title) if post.related_post else '' for post in posts],
    ]

    # 행(row) 중심 데이터 변환 (Transpose)
    table_data = list(zip(*values))

    return render(request, 'export.html', {
      **daos.get_urls(),
        'headers': headers,
        'table_data': table_data,
    })

  # 페이지네이션
  last_page = posts.count() // page_items + 1
  posts = posts[(page - 1) * page_items:page * page_items]
  search_posts = []

  # 게시글 정보
  for post in posts:
    search_posts.append({
      'id': post.id,
      'author': {
          'id': post.author.id,
          'nickname': post.author.first_name,
          'partner_name': post.author.last_name,
          'level': daos.select_level(post.author.level.level),
          'account_type': post.author.groups.all()[0].name,
      },
      'related_post': {
          'id': post.related_post.id,
          'title': post.related_post.title,
      } if post.related_post else None,
      'boards': [{
          'id': board.id,
          'name': board.name,
      } for board in post.boards.all()],
      'board_ids': ','.join([str(board.id) for board in post.boards.all()]),
      'title': post.title,
      'image': '/media/' + str(post.image) if post.image else None,
      'view_count': post.view_count,
      'like_count': post.like_count,
      'created_at': datetime.datetime.strftime(post.created_at, '%Y-%m-%d %H:%M'),
      'comment_count': models.COMMENT.objects.filter(post=post).count(),
    })

  return render(request, 'supervisor/post.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'boards': boards, # 게시판 정보
    'posts': search_posts, # 검색된 게시글 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
    'status': boards, # 게시판 별 통계 데이터. 게시판 별로 게시글 수, 댓글 수, 조회수, 좋아요 수 제공
  })

# 게시글 수정
def post_edit(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)
  if 'post' not in account['subsupervisor_permissions']:
    return redirect(settings.SUPERVISOR_URL)

  # 데이터 가져오기
  post_id = request.GET.get('post_id')
  post = daos.select_post(post_id)
  if not post:
    return redirect(settings.SUPERVISOR_URL + '/supervisor/post')

  # 게시글 수정
  if request.method == 'POST':
    # 데이터 가져오기
    title = request.POST.get('title')
    content = request.POST.get('content')
    image = request.FILES.get('image')
    search_weight = request.POST.get('search_weight')
    view_count = request.POST.get('view_count')
    like_count = request.POST.get('like_count')
    daos.update_post(
      post_id=post_id,
      title=title,
      content=content,
      image=image,
      search_weight=search_weight,
      view_count=view_count,
      like_count=like_count,
    )
    return JsonResponse({'result': 'success'})

  return render(request, 'supervisor/edit.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'post': post,
  })

# 여행지 게시글 관리 페이지
def travel(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)
  if 'travel' not in account['subsupervisor_permissions']:
    return redirect(settings.SUPERVISOR_URL)

  # 여행지 정보 수정 요청 처리
  if request.method == 'POST':
    # 데이터 가져오기
    post_id = request.POST.get('post_id')
    place_status = request.POST.get('place_status')
    post_search_weight = request.POST.get('search_weight')
    ad_start_at = request.POST.get('ad_start_at')
    ad_end_at = request.POST.get('ad_end_at')
    place_info_note = request.POST.get('place_info_note')
    daos.update_post(
      post_id=post_id,
      search_weight=post_search_weight,
    )
    daos.update_place_info(
      post_id=post_id,
      status=place_status,
      ad_start_at=ad_start_at,
      ad_end_at=ad_end_at,
      note=place_info_note,
    )
    # 통계 데이터 생성
    if place_status == 'ad':
      daos.create_statistic('place_on_ad')
    elif post_search_weight:
      if int(post_search_weight) > 0:
        daos.create_statistic('place_ad_request')
    return JsonResponse({'result': 'success'})

  # 통계 데이터 가져오기
  tab = request.GET.get('tab', 'noAdTab') # noAdTab, weightAdTab, statusAdTab
  posts = models.POST.objects.prefetch_related(
    'boards'
  ).select_related(
    'author', 'place_info'
  ).prefetch_related(
    'place_info__categories'
  ).filter(
    place_info__isnull=False
  ).order_by('-created_at')

  # 데이터 가져오기
  search_title = request.GET.get('title')
  search_board_id = request.GET.get('board_id')
  search_author = request.GET.get('author')
  search_category_id = request.GET.get('category_id')
  search_address = request.GET.get('address')
  search_place_status = request.GET.get('place_status')
  page = int(request.GET.get('page', '1'))
  page_items = int(request.GET.get('page_items', '50'))

  # 쿼리 생성
  query = Q()
  if tab == 'noAdTab':
    query &= Q(place_info__status='writing') | Q(place_info__status='active') | Q(place_info__status='pending')
    query &= Q(search_weight=0)
  elif tab == 'weightAdTab':
    query &= Q(search_weight__gt=0) & Q(place_info__status='active')
  elif tab == 'statusAdTab':
    query &= Q(place_info__status='ad')
  if search_title: # 제목 또는 내용을 검색하도록 수정됨
    query &= Q(title__contains=search_title)
    query |= Q(content__contains=search_title)
  if search_board_id:
    query &= Q(boards__id__in=[search_board_id])
  if search_author:
    query &= Q(author__username=search_author)
    query &= Q(author__first_name=search_author)
    query &= Q(author__last_name=search_author)
  if search_category_id:
    query &= Q(place_info__categories__id__in=[search_category_id])
  if search_address:
    query &= Q(place_info__address__contains=search_address)
  if search_place_status:
    query &= Q(place_info__status=search_place_status)
  posts = posts.filter(query)
  search_posts = posts.filter(query).annotate(
    ad_priority=Case(
        When(place_info__status='ad', then=Value(0)),   # 'ad' 상태일 때 우선순위 0
        When(place_info__status='active', then=Value(1)), # 'active' 상태일 때 우선순위
        default=Value(2),                                # 그 외는 우선순위 1
        output_field=IntegerField(),
    )
).order_by('ad_priority', '-search_weight', '-created_at')

  # export
  if request.GET.get('export'):
    headers = ['id', 'title', 'board', 'category', 'author_nickname', 'author_partner_name', 'open_info', 'location_info', 'search_weight', 'status', 'ad_start_at', 'ad_end_at', 'view_count', 'like_count', 'created_at']
    values = [
        [str(post.id) for post in search_posts],
        [post.title for post in search_posts],
        [str(post.boards.all().last().name) for post in search_posts],
        [str(post.place_info.categories.all().last().name) for post in search_posts],
        [str(post.author.first_name) for post in search_posts],
        [str(post.author.last_name) for post in search_posts],
        [post.place_info.open_info for post in search_posts],
        [post.place_info.location_info for post in search_posts],
        [str(post.search_weight) for post in search_posts],
        [post.place_info.status for post in search_posts],
        [datetime.datetime.strftime(post.place_info.ad_start_at, '%Y-%m-%d') if post.place_info.ad_start_at else '' for post in search_posts],
        [datetime.datetime.strftime(post.place_info.ad_end_at, '%Y-%m-%d') if post.place_info.ad_end_at else '' for post in search_posts],
        [str(post.view_count) for post in search_posts],
        [str(post.like_count) for post in search_posts],
        [datetime.datetime.strftime(post.created_at, '%Y-%m-%d %H:%M') for post in search_posts],
    ]

    # 행(row) 중심 데이터 변환 (Transpose)
    table_data = list(zip(*values))

    return render(request, 'export.html', {
        **daos.get_urls(),
        'headers': headers,
        'table_data': table_data,
    })

  # 페이지네이션
  last_page = search_posts.count() // page_items + 1
  search_posts = search_posts[(page - 1) * page_items:page * page_items]
  posts = []

  # 게시글 정보
  for post in search_posts:
    posts.append({
      'id': post.id,
      'author': {
          'id': post.author.id,
          'partner_name': post.author.first_name,
      },
      'place_info': {
          'categories': [{
              'id': c.id,
              'name': c.name,
          } for c in post.place_info.categories.all()],
          'category_ids': [c.id for c in post.place_info.categories.all()],
          'location_info': post.place_info.location_info,
          'open_info': post.place_info.open_info,
          'status': post.place_info.status,
          'note': post.place_info.note,
          'ad_start_at': datetime.datetime.strftime(post.place_info.ad_start_at, '%Y-%m-%d'),
          'ad_end_at': datetime.datetime.strftime(post.place_info.ad_end_at, '%Y-%m-%d'),
      } if post.place_info else None,
      'boards': [{
          'id': board.id,
          'name': board.name,
      } for board in post.boards.all()],
      'board_ids': ','.join([str(board.id) for board in post.boards.all()]),
      'title': post.title,
      'image': '/media/' + str(post.image) if post.image else None,
      'view_count': post.view_count,
      'like_count': post.like_count,
      'created_at': datetime.datetime.strftime(post.created_at, '%Y-%m-%d %H:%M'),
      'comment_count': models.COMMENT.objects.filter(post=post).count(),
      'review_count': models.POST.objects.filter(related_post=post).count(),
      'search_weight': post.search_weight,
    })

  # 카테고리 정보
  boards = daos.make_board_tree(board_type='travel')
  categories = daos.make_category_tree(status=True)

  return render(request, 'supervisor/travel.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'posts': posts, # 검색된 게시글 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
    'travel_boards': boards, # 게시판 정보
    'categories': categories, # 카테고리 정보
  })

# 여행지 게시글 수정
def travel_edit(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)
  if 'travel' not in account['subsupervisor_permissions']:
    return redirect(settings.SUPERVISOR_URL)

  # 데이터 가져오기
  post_id = request.GET.get('post_id')
  post = daos.select_post(post_id)

  # 여행지 게시글 수정
  if request.method == 'POST':
    title = request.POST.get('title')
    content = request.POST.get('content')
    image = request.FILES.get('image')
    search_weight = request.POST.get('search_weight')
    view_count = request.POST.get('view_count')
    like_count = request.POST.get('like_count')
    category_ids = request.POST.get('category_ids')
    location_info = request.POST.get('location_info')
    open_info = request.POST.get('open_info')
    address = request.POST.get('address')
    board_ids = request.POST.get('board_ids')
    # 데이터 업데이트
    daos.update_post(
      post_id=post_id,
      title=title,
      content=content,
      image=image,
      search_weight=search_weight,
      view_count=view_count,
      like_count=like_count,
      board_ids=board_ids
    )
    daos.update_place_info(
      post_id=post_id,
      category_ids=category_ids,
      location_info=location_info,
      open_info=open_info,
      address=address,
    )
    return JsonResponse({'result': 'success'})

  # 카테고리 정보
  boards = daos.make_board_tree(board_type='travel')
  categories = daos.make_category_tree()
  board = post['boards'][-1]
  board['id'] = str(board['id'])
  category = post['place_info']['categories'][-1]
  category['id'] = str(category['id'])

  return render(request, 'supervisor/travel_edit.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'post': post,
    'categories': categories,
    'boards': boards,
    'board': board,
    'category': category,
  })

# 쿠폰 관리 페이지
def coupon(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)
  if 'coupon' not in account['subsupervisor_permissions']:
    return redirect(settings.SUPERVISOR_URL)

  # 데이터 가져오기
  tab = request.GET.get('tab', 'couponTab') # coupopn, history
  page = int(request.GET.get('page', 1))
  search_coupon_code = request.GET.get('code') # 쿠폰 이름 검색
  search_coupon_name = request.GET.get('name', '') # 쿠폰 소유자 검색
  search_create_account = request.GET.get('create_account') # 쿠폰 생성자 검색
  search_own_account = request.GET.get('own_account') # 쿠폰 소유자 검색
  page_items = int(request.GET.get('page_items', '50'))
  coupons = models.COUPON.objects.select_related(
    'related_post', 'create_account', 'own_account'
  ).all().order_by('-created_at')

  # status
  status = {
    'active': coupons.filter(status='active').count(),
    'used': coupons.filter(status='used').count(),
    'expired': coupons.filter(status='expired').count(),
    'deleted': coupons.filter(status='deleted').count(),
  }

  # 쿠폰 검색
  query = Q()
  if tab == 'couponTab':
    query &= Q(status='active')
  elif tab == 'historyTab':
    query &= ~Q(status='active')
  if search_coupon_code:
    query &= Q(code=search_coupon_code)
  if search_coupon_name:
    query &= Q(name__contains=search_coupon_name)
  if search_create_account:
    create_account = models.ACCOUNT.objects.filter(
      Q(first_name=search_create_account) | Q(last_name=search_create_account) | Q(username=search_create_account)
    ).first()
    if create_account:
      query &= Q(create_account=create_account)
  if search_own_account:
    own_account = models.ACCOUNT.objects.filter(
      Q(first_name=search_own_account) | Q(username=search_own_account)
    ).first()
    if own_account:
      query &= Q(own_account=own_account)
  coupons = coupons.filter(query)

  if request.GET.get('export'):
    headers = ['code', 'name', 'image', 'content', 'required_mileage', 'expire_at', 'status', 'post', 'create_account']
    values = [
        [coupon.code for coupon in coupons],
        [coupon.name for coupon in coupons],
        [str(coupon.image) for coupon in coupons],
        [coupon.content for coupon in coupons],
        [coupon.required_mileage for coupon in coupons],
        [coupon.expire_at for coupon in coupons],
        [coupon.status for coupon in coupons],
        [coupon.related_post.title for coupon in coupons],
        [coupon.create_account.last_name for coupon in coupons],
    ]

    # 행(row) 중심 데이터 변환 (Transpose)
    table_data = list(zip(*values))

    return render(request, 'export.html', {
        **daos.get_urls(),
        'headers': headers,
        'table_data': table_data,
    })

  # 페이지네이션
  last_page = coupons.count() // page_items + 1
  coupons = coupons[(page - 1) * page_items:page * page_items]
  coupon_data = []

  # 쿠폰 정보
  for coupon in coupons:
    coupon_data.append({
      'code': coupon.code,
      'name': coupon.name,
      'image': '/media/' + str(coupon.image) if coupon.image else None,
      'content': coupon.content,
      'required_mileage': coupon.required_mileage,
      'expire_at': datetime.datetime.strftime(coupon.expire_at, '%Y-%m-%d'),
      'status': coupon.status,
      'related_post': {
        'id': coupon.related_post.id,
        'title': coupon.related_post.title,
      },
      'create_account': {
        'id': coupon.create_account.id,
        'partner_name': coupon.create_account.last_name,
        'account_type': coupon.create_account.groups.all()[0].name,
      },
      'own_account': {
        'id': coupon.own_account.id,
        'nickname': coupon.own_account.first_name,
      } if coupon.own_account else None,
    })

  return render(request, 'supervisor/coupon.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'status': status, # 쿠폰 종류(탭) 별 통계 데이터
    'coupons': coupon_data, # 검색된 쿠폰 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
  })

# 쪽지 관리 페이지
def message(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)
  if 'message' not in account['subsupervisor_permissions']:
    return redirect(settings.SUPERVISOR_URL)

  # data
  tab = request.GET.get('tab', 'inboxTab') # inbox, outbox
  message_type = request.GET.get('message_type', 'user_question') # user_question, partner_question, request_ad, request_coupon
  page = int(request.GET.get('page', '1'))
  search_message_title = request.GET.get('message_title', '')
  search_message_receiver = request.GET.get('message_receiver', '')
  page_items = int(request.GET.get('page_items', '50'))

  # 통계 데이터 가져오기
  if tab == 'inboxTab':
    messages = models.MESSAGE.objects.select_related(
      'sender', 'receive', 'include_coupon'
    ).filter(receive__isnull=True).order_by('-created_at')
  else:
    messages = models.MESSAGE.objects.select_related(
      'sender', 'receive', 'include_coupon'
    ).filter(sender__isnull=True).order_by('-created_at')
  status = {
    'user_question_read': messages.filter(message_type='user_question', is_read=True).count(),
    'user_question_unread': messages.filter(message_type='user_question', is_read=False).count(),
    'partner_question_read': messages.filter(message_type='partner_question', is_read=True).count(),
    'partner_question_unread': messages.filter(message_type='partner_question', is_read=False).count(),
    'request_ad_read': messages.filter(message_type='request_ad', is_read=True).count(),
    'request_ad_unread': messages.filter(message_type='request_ad', is_read=False).count(),
    'request_coupon_read': messages.filter(message_type='request_coupon', is_read=True).count(),
    'request_coupon_unread': messages.filter(message_type='request_coupon', is_read=False).count(),
  }

  # 쿼리 생성
  query = Q()
  if message_type:
    query &= Q(message_type=message_type)
  if search_message_title:
    query &= Q(title__contains=search_message_title)
  if search_message_receiver:
    receiver = models.ACCOUNT.objects.filter(
      Q(first_name=search_message_receiver) | Q(last_name=search_message_receiver)
    ).first()
    if receiver:
      query &= Q(receive=receiver)
  messages = messages.filter(query)

  # export
  if request.GET.get('export'):
    headers = ['id', 'title', 'is_read', 'created_at', 'include_coupon_code', 'sender', 'receiver']
    values = [
      [m.id for m in messages],
      [m.title for m in messages],
      [m.is_read for m in messages],
      [datetime.datetime.strftime(m.created_at, '%Y-%m-%d %H:%M') for m in messages],
      [m.include_coupon.code if m.include_coupon else '' for m in messages],
      ['관리자' if m.sender is None else m.sender.first_name for m in messages],
      ['관리자' if m.receive is None else m.receive.first_name for m in messages],
    ]

    # 행(row) 중심 데이터 변환 (Transpose)
    table_data = list(zip(*values))

    return render(request, 'export.html', {
      **daos.get_urls(),
      'headers': headers,
      'table_data': table_data
    })

  # 페이지네이션
  last_page = messages.count() // page_items + 1
  messages = messages[(page - 1) * page_items:page * page_items]
  message_data = []

  # 메시지 정보
  for msg in messages:
    message_data.append({
      'id': msg.id,
      'sender_account': {
        'id': msg.sender.id,
        'username': msg.sender.username,
        'nickname': msg.sender.first_name,
      } if msg.sender else {'id': account['id'], 'nickname': '관리자', 'account_type': 'supervisor', 'username': 'admin'},
      'receive_account': {
        'id': msg.receive.id,
        'username': msg.receive.username,
        'nickname': msg.receive.first_name,
      } if msg.receive else {'id': account['id'], 'nickname': '관리자', 'account_type': 'supervisor', 'username': 'admin'},
      'title': msg.title,
      'content': msg.content,
      'image': '/media/' + str(msg.image) if msg.image else None,
      'include_coupon': {
          'code': msg.include_coupon.code,
          'name': msg.include_coupon.name,
          'required_mileage': msg.include_coupon.required_mileage,
          'expire_at': datetime.datetime.strftime(msg.include_coupon.expire_at, '%Y-%m-%d'),
      } if msg.include_coupon else None,
      'is_read': msg.is_read,
      'created_at': datetime.datetime.strftime(msg.created_at, '%Y-%m-%d %H:%M'),
    })

  return render(request, 'supervisor/message.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'status': status,
    'messages': message_data,
    'last_page': last_page
  })

# 배너 관리 페이지
def banner(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)
  if 'banner' not in account['subsupervisor_permissions']:
    return redirect(settings.SUPERVISOR_URL)

  # POST 요청 처리
  if request.method == 'POST':
    # 데이터 가져오기
    banner_id = request.GET.get('banner')
    print(banner_id)
    print(request.POST.dict())
    if banner_id:
      daos.update_banner(
        banner=banner_id,
        location=request.POST.get('location'),
        image=request.FILES.get('image'),
        link=request.POST.get('link', ''),
        status=request.POST.get('status'),
        display_weight=request.POST.get('display_weight'),
      )
    else:
      daos.create_banner(
        location=request.POST.get('location'),
        image=request.FILES.get('image'),
        link=request.POST.get('link'),
        status=request.POST.get('status'),
        display_weight=request.POST.get('display_weight')
      )
    return JsonResponse({'result': 'success'})
  # DELETE 요청 처리
  if request.method == 'DELETE':
    banner_id = request.GET.get('banner')
    daos.delete_banner(banner_id)
    return JsonResponse({'result': 'success'})

  # 데이터 가져오기
  tab = request.GET.get('tab', 'topTab') # topTab, sideTab, postTab
  if tab == 'postTab':
    banners= daos.select_banners('post')
  elif tab == 'sideTab':
    banners = daos.select_banners('side')
  else:
    banners = daos.select_banners('top')

  return render(request, 'supervisor/banner.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'banners': banners,
  })

# 레벨 관리 페이지
def level(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)
  if 'level' not in account['subsupervisor_permissions']:
    return redirect(settings.SUPERVISOR_URL)

  # 레벨 생성 및 수정 요청 처리
  if request.method == 'POST':
    level_id = request.POST.get('level')
    if level_id:
      daos.update_level(
        level=level_id,
        image=request.FILES.get('image', None),
        text=request.POST.get('text', ''),
        text_color=request.POST.get('text_color', ''),
        background_color=request.POST.get('background_color', ''),
        required_exp=request.POST.get('exp', ''),
      )
    else:
      daos.create_level(
        image=request.FILES.get('image', None),
        text=request.POST.get('text', ''),
        text_color=request.POST.get('text_color', ''),
        background_color=request.POST.get('background_color', ''),
        required_exp=request.POST.get('exp', ''),
      )
    return JsonResponse({'result': 'success'})

  # 레벨 정보 가져오기
  levels = daos.select_all_levels()

  return render(request, 'supervisor/level.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'levels': levels,
  })

# 시스템 설정 페이지
def setting(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.SUPERVISOR_URL)
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL)
  if 'setting' not in account['subsupervisor_permissions']:
    return redirect(settings.SUPERVISOR_URL)

  # 설정 정보 변경 요청 처리
  if request.method == 'POST':
    daos.update_server_setting('service_name', request.POST.get('service_name'))
    daos.update_server_setting('site_logo', request.POST.get('site_logo'))
    daos.update_server_setting('company_info', request.POST.get('company_info'))
    daos.update_server_setting('terms', request.POST.get('terms'))
    daos.update_server_setting('register_point', request.POST.get('register_point'))
    daos.update_server_setting('attend_point', request.POST.get('attend_point'))
    daos.update_server_setting('post_point', request.POST.get('post_point'))
    daos.update_server_setting('review_point', request.POST.get('review_point'))
    daos.update_server_setting('comment_point', request.POST.get('comment_point'))
    return JsonResponse({'result': 'success'})

  return render(request, 'supervisor/setting.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'settings': {
      'service_name': daos.select_server_setting('service_name'),
      'site_logo': daos.select_server_setting('site_logo'),
      'company_info': daos.select_server_setting('company_info'),
      'terms': daos.select_server_setting('terms'),
      'register_point': daos.select_server_setting('register_point'),
      'attend_point': daos.select_server_setting('attend_point'),
      'post_point': daos.select_server_setting('post_point'),
      'review_point': daos.select_server_setting('review_point'),
      'comment_point': daos.select_server_setting('comment_point'),
    },
  })