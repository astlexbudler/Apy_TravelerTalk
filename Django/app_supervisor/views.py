import datetime
import math
import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, get_user_model
from django.db.models import Q
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

  return redirect('/supervisor/supervisor')

# 관리자 메인 페이지
def index(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if account['account_type'] not in ['supervisor', 'subsupervisor']:
    return redirect('/')

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
    Q(status='used') | Q(status='expired') | Q(status='deleted')
  ).count()
  coupon_request_message_count = models.MESSAGE.objects.filter(
    title__startswith='쿠폰 요청:',
    is_read=False,
    to_account='supervisor'
  ).count()

  # 여행지 게시글 광고 정보
  place_on_ad_count = models.PLACE_INFO.objects.filter(
    status='ad'
  ).count()
  place_ad_request_count = models.PLACE_INFO.objects.filter(
    status='pending'
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
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if 'user' not in account['subsupervisor_permissions']:
    return redirect('/')

  # 아이피 차단
  if request.method == 'POST' and request.GET.get('block_ip'):
    ip_address = request.POST['ip']
    daos.create_blocked_ip(ip_address)
    return JsonResponse({'result': 'success'})

  # 아이피 차단 해제
  if request.method == 'POST' and request.GET.get('unblock_ip'):
    ip_address = request.POST['ip']
    daos.delete_blocked_ip(ip_address)
    return JsonResponse({'result': 'success'})

  '''
  if request.method == 'POST' and request.GET.get('create_user'):
    id = request.POST['id']
    password = request.POST['password']
    nickname = request.POST['nickname']
    number = int(request.POST.get('number', '1'))

    user_group = Group.objects.get(name='user')
    level = models.LEVEL_RULE.objects.get(level=1)

    # number가 2 이상인 경우, 반복
    if number > 1:
      for i in range(number):
        repeat_id = id + str(i)
        repeat_nickname = nickname + str(i)
        id_exist = models.ACCOUNT.objects.filter(username=repeat_id).exists()
        nickname_exist = models.ACCOUNT.objects.filter(first_name=repeat_nickname).exists()
        if not id_exist and not nickname_exist:
          account = models.ACCOUNT.objects.create_user(
            username = repeat_id,
            first_name = repeat_nickname,
            note = '관리자에 의해 생성됨.',
            level = level,
            recent_ip = '',
          )
          account.set_password(password)
          account.save()
          account.groups.add(user_group)
          account.save()
    else:
      id_exist = models.ACCOUNT.objects.filter(username=id).exists()
      nickname_exist = models.ACCOUNT.objects.filter(first_name=nickname).exists()
      if not id_exist and not nickname_exist:
        account = models.ACCOUNT.objects.create_user(
          username = id,
          first_name = nickname,
          note = '관리자에 의해 생성됨.',
          level = level,
          recent_ip = '',
        )
        account.set_password(password)
        account.save()
        account.groups.add(user_group)
        account.save()

    return JsonResponse({'result': 'success'})
  '''

  # 부관리자 신규 생성 처리
  if request.method == 'POST' and request.GET.get('create_subsupervisor'):
    id = request.POST['id']
    password = request.POST['password']
    daos.create_account(
      username=id,
      password=password,
      first_name='관리자' + ''.join(random.choices(string.ascii_letters + string.digits, k=6)),
      last_name='',
      email='',
      tel='',
      account_type='subsupervisor',
    )
    return JsonResponse({'result': 'success'})

  # data
  tab = request.GET.get('tab', 'userTab') # user, dame, partner, supervisor
  page = int(request.GET.get('page', '1'))
  search_user_dame = request.GET.get('dame', '')
  search_account_id = request.GET.get('account_id', '')
  search_account_nickname = request.GET.get('account_nickname', '')
  search_account_level_at_least = int(request.GET.get('account_level_at_least', '0'))
  search_account_status = request.GET.get('account_status', '')
  search_account_ip = request.GET.get('account_ip', '')
  search_account_mileage_at_least = int(request.GET.get('account_mileage_at_least', '0'))

  # 계정 타입별로 계정 통계 가져오기
  # 관리자 계정 탭은 별도의 통계 없음.
  # 파트너는 각 카테고리면 파트너 계정 통계 제공
  # 사용자는 사용자 및 여성 회원의 계정 통계 제공
  all_accounts = models.ACCOUNT.objects.prefetch_related(
    'groups'
  ).select_related(
    'level'
  ).all().order_by('date_joined')

  # status
  if tab == 'supervisorTab': # 관리자 검색 탭일 경우, 별도의 사용자 통계 기능 없음.
    status = {}
  elif tab == 'userTab': # 사용자 검색 탭일 경우, 사용자 및 여성회원 정보 제공
    dame_accounts = all_accounts.filter(
      groups__name='dame'
    )
    user_accounts = all_accounts.filter(
      groups__name='user'
    )
    status = {
      'user': {
        'active': user_accounts.filter(status='active').count(),
        'pending': 0,
        'deleted': user_accounts.filter(status='deleted').count(),
        'blocked': user_accounts.filter(status='blocked').count(),
      },
      'dame': {
        'active': dame_accounts.filter(status='active').count(),
        'pending': dame_accounts.filter(status='pending').count(),
        'deleted': dame_accounts.filter(status='deleted').count(),
        'blocked': dame_accounts.filter(status='blocked').count(),
      }
    }
  elif tab == 'partnerTab': # 파트너 검색 탭일 경우, 파트너 정보 제공
    partner_accounts = all_accounts.filter(
      Q(groups__name='partner')
    )
    status = {
      'partner': {
        'active': partner_accounts.filter(status='active').count(),
        'pending': partner_accounts.filter(status='pending').count(),
        'deleted': partner_accounts.filter(status='deleted').count(),
        'blocked': partner_accounts.filter(status='blocked').count(),
      }
    }

  # 사용자 검색
  if tab == 'userTab': # 사용자 탭일 경우, user와 dame을 같이 검색
    sats = all_accounts.select_related('level').filter(
      Q(username__contains=search_account_id),
      Q(first_name__contains=search_account_nickname),
      Q(level__level__gte=search_account_level_at_least),
      Q(status__contains=search_account_status),
      Q(recent_ip__contains=search_account_ip),
      Q(mileage__gte=search_account_mileage_at_least)
    )
    if search_user_dame == 'user':
      sats = sats.filter(
        Q(groups__name='user')
      )
    elif search_user_dame == 'dame':
      sats = sats.filter(
        Q(groups__name='dame'),
      )
    else:
      sats = sats.filter(
        Q(groups__name='user') | Q(groups__name='dame'),
      )
  elif tab == 'supervisorTab': # 관리자 탭일 경우, 관리자만 검색
    sats = all_accounts.filter(
      Q(groups__name__in=['supervisor', 'subsupervisor']),
      Q(username__contains=search_account_id),
      Q(first_name__contains=search_account_nickname),
      Q(recent_ip__contains=search_account_ip),
    )
  elif tab == 'partnerTab': # 파트너 탭일 경우, 파트너만 검색
    sats = all_accounts.filter(
      Q(groups__name='partner'),
      Q(username__contains=search_account_id),
      Q(first_name__contains=search_account_nickname),
      Q(level__level__gte=search_account_level_at_least),
      Q(status__contains=search_account_status),
      Q(recent_ip__contains=search_account_ip),
      Q(mileage__gte=search_account_mileage_at_least)
    )

  # 만약 출력 요청일 경우, 모든 줄 출력
  if request.GET.get('print'):
    return render(request, 'supervisor/account_print.html', {
      **daos.get_urls(),
      'accounts': sats,
    })

  # export
  if request.GET.get('export'):
    headers = ['아이디', '닉네임', '파트너이름', '이메일', '연락처', '계정 종류', '가입일', '마지막 로그인', '상태', '노트', '마일리지', '경험치', '부관리자 권한', '최근 접속 IP', '레벨']
    values = [
      [acnt.username for acnt in sats],
      [acnt.first_name for acnt in sats],
      [acnt.last_name for acnt in sats],
      [acnt.email for acnt in sats],
      [acnt.tel for acnt in sats],
      [[group.name for group in acnt.groups.all()] for acnt in sats],
      [acnt.date_joined for acnt in sats],
      [acnt.last_login for acnt in sats],
      [acnt.status for acnt in sats],
      [acnt.note for acnt in sats],
      [acnt.mileage for acnt in sats],
      [acnt.exp for acnt in sats],
      [acnt.subsupervisor_permissions for acnt in sats],
      [acnt.recent_ip for acnt in sats],
      [acnt.level.level for acnt in sats],
    ]
    table_data = list(zip(*values))
    return render(request, 'export.html', {
      **daos.get_urls(),
      'headers': headers,
      'table_data': table_data,
    })

  last_page = sats.count() // 20 + 1 # 20개씩 표시
  search_accounts = []
  for account in sats[(page - 1) * 20:page * 20]:

    # 계정 정보
    search_accounts.append({
      'id': account.id,
      'username': account.username,
      'nickname': account.first_name,
      'partner_name': account.last_name,
      'email': account.email,
      'tel': account.tel,
      'account_type': [group.name for group in account.groups.all()],
      'date_joined': datetime.datetime.strftime(account.date_joined, '%Y-%m-%d %H:%M:%S'),
      'last_login': datetime.datetime.strftime(account.last_login, '%Y-%m-%d %H:%M:%S') if account.last_login else '',
      'status': account.status,
      'note': account.note,
      'mileage': account.mileage,
      'exp': account.exp,
      'subsupervisor_permissions': account.subsupervisor_permissions,
      'recent_ip': account.recent_ip,
      'level': {
        'level': account.level.level,
        'image': '/media/' + account.level.image.url if account.level.image else None,
        'text': account.level.text,
        'text_color': account.level.text_color,
        'background_color': account.level.background_color,
      } if account.level else None,
    })

  # 차단 IP 목록
  blocked_ips = [{
    'ip': blocked_ip.ip
  } for blocked_ip in models.BLOCKED_IP.objects.all()]

  return render(request, 'supervisor/account.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'accounts': search_accounts, # 검색된 계정 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
    'status': status, # 사용자 종류(탭) 별 통계 데이터(관리자는 없음)
    'blocked_ips': blocked_ips, # 차단 IP 목록
  })

# 프로필
def profile(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if 'user' not in account['subsupervisor_permissions']:
    return redirect('/')

  # 프로필 수정
  if request.method == 'POST':
    nickname = request.POST.get('nickname', '')
    email = request.POST.get('email', '')
    tel = request.POST.get('tel', '')
    password = request.POST.get('password', '')
    new_password = request.POST.get('new_password', '')
    new_password_confirm = request.POST.get('new_password_confirm', '')
    if password and new_password and new_password_confirm:
      if not request.user.check_password(password):
        return JsonResponse({'result': 'fail', 'message': '비밀번호가 일치하지 않습니다.'})
      if new_password != new_password_confirm:
        return JsonResponse({'result': 'fail', 'message': '새로운 비밀번호가 일치하지 않습니다.'})
      request.user.set_password(new_password)
      request.user.save()
    if nickname:
      request.user.first_name = nickname
    if email:
      request.user.email = email
    if tel:
      request.user.tel = tel
    request.user.save()
    return JsonResponse({'result': 'success'})

  # data
  account_id = request.GET.get('account_id', '')

  # 계정 정보
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
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if 'user' not in account['subsupervisor_permissions']:
    return redirect('/')

  # data
  page = int(request.GET.get('page', '1'))
  profile_id = request.GET.get('account_id', '')

  # 활동 정보
  activities, last_page = daos.select_account_activities(profile_id, page)
  status = daos.get_account_activity_stats(profile_id)

  return render(request, 'supervisor/activity.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'activities': activities,
    'status': status,
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
  })

# 게시글 관리 페이지
def post(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if 'post' not in account['subsupervisor_permissions']:
    return redirect('/')

  # 새 게시판 생성 요청 또는 게시판 수정 요청 처리
  if request.method == 'POST' and request.GET.get('board'):
    board_id = request.POST.get('board_id')
    board_name = request.POST.get('board_name')
    board_type = request.POST.get('board_type')
    parent_board_id = request.POST.get('parent_board_id')
    display_weight = request.POST.get('display_weight')
    level_cut = request.POST.get('level_cut')
    display_groups = str(request.POST.get('display_groups', '')).split(',')
    enter_groups = str(request.POST.get('enter_groups', '')).split(',')
    write_groups = str(request.POST.get('write_groups', '')).split(',')
    comment_groups = str(request.POST.get('comment_groups', '')).split(',')

    if board_id:
      daos.update_board(
        board_id=board_id,
        parent_board_id=parent_board_id,
        name=board_name,
        board_type=board_type,
        display_groups=Group.objects.filter(name__in=display_groups),
        enter_groups=Group.objects.filter(name__in=enter_groups),
        write_groups=Group.objects.filter(name__in=write_groups),
        comment_groups=Group.objects.filter(name__in=comment_groups),
        display_weight=display_weight,
        level_cut=level_cut,
      )
    else:
      daos.create_board(
        parent_board_id=parent_board_id,
        name=board_name,
        board_type=board_type,
        display_groups=Group.objects.filter(name__in=display_groups),
        enter_groups=Group.objects.filter(name__in=enter_groups),
        write_groups=Group.objects.filter(name__in=write_groups),
        comment_groups=Group.objects.filter(name__in=comment_groups),
        display_weight=display_weight,
        level_cut=level_cut,
      )
    return JsonResponse({'result': 'success'})

  # 게시판 삭제 요청 처리
  if request.method == 'DELETE' and request.GET.get('board'):
    board_id = request.GET.get('board_id', '')
    daos.delete_board(board_id)
    return JsonResponse({'result': 'success'})

  # data
  page = int(request.GET.get('page', '1'))
  search_post_title = request.GET.get('post_title', '')
  search_board_id = request.GET.get('board_id', '')
  search_author_id = request.GET.get('author_id', '')

  # status
  # 각 게시판 별 게시글 수와 댓글 수, 조회수, 좋아요 수 통계 제공
  all_post = models.POST.objects.exclude(
    author__isnull=True
  ).prefetch_related(
    'boards'
  ).select_related(
    'author', 'place_info', 'related_post'
  ).prefetch_related(
    'place_info__categories'
  ).all()
  boards = models.BOARD.objects.exclude(
    Q(board_type='greeting') | Q(board_type='attendance')
  ).prefetch_related('display_groups', 'enter_groups', 'write_groups', 'comment_groups').all().order_by('-display_weight')
  board_dict = {
    board.name: {
      'id': board.id,
      'name': board.name,
      'board_type': board.board_type,
      'total_views': int(math.fsum([post.view_count for post in models.POST.objects.filter(Q(boards__id__in=str(board.id)))])),
      'total_posts': models.POST.objects.filter(Q(boards__id__in=str(board.id))).count(),
      'level_cut': board.level_cut,
      'display_weight': board.display_weight,
      'display': [g.name for g in board.display_groups.all()],
      'enter': [g.name for g in board.enter_groups.all()],
      'write': [g.name for g in board.write_groups.all()],
      'comment': [g.name for g in board.comment_groups.all()],
      'children': [],
    } for board in boards if not board.parent_board
  }
  for board in boards:
    if board.parent_board:
      if board_dict.get(board.parent_board.name):
        board_dict[board.parent_board.name]['children'].append({
          'id': board.id,
          'name': board.name,
          'board_type': board.board_type,
          'total_views': int(math.fsum([post.view_count for post in models.POST.objects.filter(Q(boards__id__in=[board.id]))])),
          'level_cut': board.level_cut,
          'display_weight': board.display_weight,
          'total_posts': models.POST.objects.filter(Q(boards__id__in=[board.id])).count(),
          'display': [g.name for g in board.display_groups.all()],
          'enter': [g.name for g in board.enter_groups.all()],
          'write': [g.name for g in board.write_groups.all()],
          'comment': [g.name for g in board.comment_groups.all()],
          'children': [],
        })
      else:
        loop = True
        for key in board_dict.keys():
          for child in board_dict[key]['children']:
            if not loop:
              break
            if str(child['name']) == str(board.parent_board.name):
              child['children'].append({
                'id': board.id,
                'name': board.name,
                'board_type': board.board_type,
                'total_views': int(math.fsum([post.view_count for post in models.POST.objects.filter(Q(boards__id__in=[board.id]))])),
                'total_posts': models.POST.objects.filter(Q(boards__id__in=[board.id])).count(),
                'level_cut': board.level_cut,
                'display_weight': board.display_weight,
                'display': [g.name for g in board.display_groups.all()],
                'enter': [g.name for g in board.enter_groups.all()],
                'write': [g.name for g in board.write_groups.all()],
                'comment': [g.name for g in board.comment_groups.all()],
                'children': [],
              })
              loop = False
            if loop:
              for grandchild in child['children']:
                if not loop:
                  break
                if str(grandchild['name']) == str(board.parent_board.name):
                  grandchild['children'].append({
                    'id': board.id,
                    'name': board.name,
                    'board_type': board.board_type,
                    'total_views': int(math.fsum([post.view_count for post in models.POST.objects.filter(Q(boards__id__in=[board.id]))])),
                    'total_posts': models.POST.objects.filter(Q(boards__id__in=[board.id])).count(),
                    'level_cut': board.level_cut,
                    'display_weight': board.display_weight,
                    'display': [g.name for g in board.display_groups.all],
                    'enter': [g.name for g in board.enter_groups.all()],
                    'write': [g.name for g in board.write_groups.all()],
                    'comment': [g.name for g in board.comment_groups.all()],
                    'children': [],
                  })
                  loop = False
  boards = []
  for child in board_dict.keys():
    boards.append(board_dict[child])

  # 게시글 검색
  sps = all_post.filter(
    place_info__isnull=True,
    title__contains=search_post_title,
    author__username__contains=search_author_id,
  )

  if search_board_id: # 게시판 필터링
    sps = sps.filter(boards__id__contains=search_board_id)

  # export
  if request.GET.get('export'):
    headers = ['id', 'title', 'image', 'view_count', 'like_count', 'created_at', 'search_weight', 'board', 'author', 'place_info', 'related_post']
    values = [
        [str(post.id) for post in sps],
        [post.title for post in sps],
        [str(post.image) for post in sps],
        [str(post.view_count) for post in sps],
        [str(post.like_count) for post in sps],
        [str(post.created_at) for post in sps],
        [str(post.search_weight) for post in sps],
        [str(post.boards.all().last().name) for post in sps],
        [str(post.author.username) for post in sps],
        [str(post.place_info) for post in sps],
        [str(post.related_post) for post in sps],
    ]

    # 행(row) 중심 데이터 변환 (Transpose)
    table_data = list(zip(*values))

    return render(request, 'export.html', {
      **daos.get_urls(),
        'headers': headers,
        'table_data': table_data,
    })

  last_page = sps.count() // 20 + 1 # 20개씩 표시
  search_posts = []
  for post in sps[(page - 1) * 20:page * 20]:
    try:
      search_posts.append({
        'id': post.id,
        'title': post.title,
        'image': '/media/' + str(post.image) if post.image else None,
        'view_count': post.view_count,
        'like_count': post.like_count,
        'comment_count': models.COMMENT.objects.filter(post=post).count(),
        'created_at': datetime.datetime.strftime(post.created_at, '%Y-%m-%d %H:%M'),
        'search_weight': post.search_weight,
        'board': {
          'name': post.boards.all().last().name,
          'board_type': post.boards.all().last().board_type,
        },
        'author': {
          'id': post.author.username, # 작성자 아이디
          'nickname': post.author.first_name, # 작성자 닉네임
          'partner_name': post.author.last_name, # 작성자 파트너 이름
        },
        'related_post': { # 리뷰 게시글인 경우, 리뷰 대상 게시글 정보
          'id': post.related_post.id,
          'title': post.related_post.title,
        } if post.related_post else None,
      })
    except Exception as e:
      print(e)

  # 카테고리 정보
  categories = daos.make_category_tree()

  return render(request, 'supervisor/post.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'posts': search_posts, # 검색된 게시글 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
    'status': boards, # 게시판 별 통계 데이터. 게시판 별로 게시글 수, 댓글 수, 조회수, 좋아요 수 제공
    'categories': categories, # 카테고리 정보
  })

# 게시글 수정
def post_edit(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if 'post' not in account['subsupervisor_permissions']:
    return redirect('/')

  # 게시글 수정
  if request.method == 'POST':
    daos.update_post(
      post_id=request.GET['post_id'],
      title=request.POST.get('title'),
      content=request.POST.get('content'),
      image=request.FILES.get('image', None),
      search_weight=request.POST.get('search_weight'),
      view_count=request.POST.get('view_count'),
      like_count=request.POST.get('like_count'),
    )
    return JsonResponse({'result': 'success'})

  # 게시글 삭제
  if request.method == 'DELETE':
    daos.delete_post(request.GET['post_id'])
    return JsonResponse({'result': 'success'})

  # data
  post_id = request.GET['post_id']
  post = daos.select_post(post_id)

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
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if 'post' not in account['subsupervisor_permissions']:
    return redirect('/')

  # 여행지 정보 수정 요청 처리
  if request.method == 'POST' and request.GET.get('modify_travel_info'):
    daos.update_post(
      post_id=request.GET['post_id'],
      search_weight=request.POST.get('search_weight'),
    )
    daos.update_place_info(
      post_id=request.GET['post_id'],
      status=request.POST.get('place_status'),
      ad_start_at=request.POST.get('ad_start_at'),
      ad_end_at=request.POST.get('ad_end_at'),
      note=request.POST.get('note'),
    )
    return JsonResponse({'result': 'success'})

  # 새 카테고리 생성 요청 또는 카테고리 수정 요청 처리
  if request.method == 'POST' and request.GET.get('category'):
    category_id = request.POST.get('category_id')
    if category_id:
      daos.update_category(
        category_id=category_id,
        name=request.POST.get('name'),
        display_weight=request.POST.get('display_weight'),
      )
    else:
      daos.create_category(
        parent_category_id=request.POST.get('parent_category_id'),
        name=request.POST.get('name'),
        display_weight=request.POST.get('display_weight'),
      )
    return JsonResponse({'result': 'success'})

  # 카테고리 삭제 요청 처리
  if request.method == 'DELETE' and request.GET.get('category'):
    daos.delete_category(request.GET.get('category_id'))
    return JsonResponse({'result': 'success'})

  # data
  page = int(request.GET.get('page', '1'))
  search_post_title = request.GET.get('post_title', '')
  search_board_id = request.GET.get('board_id', '')
  search_author_id = request.GET.get('author_id', '')
  search_category_id = request.GET.get('category_id', '')
  search_address = request.GET.get('address', '')
  place_status = request.GET.get('place_status', '')

  # 여행지 정보 수정 요청 처리
  if request.method == 'POST' and request.GET.get('modify_travel_info'):
    post_id = request.POST.get('post_id', '')
    place_status = request.POST.get('place_status')
    post_search_weight = request.POST.get('post_search_weight')
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
    return JsonResponse({'result': 'success'})

  # 새 카테고리 생성 요청 또는 카테고리 수정 요청 처리
  if request.method == 'POST' and request.GET.get('category'):
    category_id = request.POST.get('category_id')
    category_name = request.POST.get('category_name')
    parent_category_id = request.POST.get('parent_category_id')
    display_weight = request.POST.get('category_weight')
    if category_id:
      daos.update_category(
        category_id=category_id,
        parent_category_id=parent_category_id,
        name=category_name,
        display_weight=display_weight,
      )
    else:
      daos.create_category(
        parent_category_id=parent_category_id,
        name=category_name,
        display_weight=display_weight,
      )
    return JsonResponse({'result': 'success'})

  # 카테고리 삭제 요청 처리
  if request.method == 'DELETE' and request.GET.get('category'):
    category_id = request.GET.get('category_id')
    daos.delete_category(category_id)
    return JsonResponse({'result': 'success'})

  # data
  page = int(request.GET.get('page', '1'))
  search_post_title = request.GET.get('post_title', '')
  search_board_id = request.GET.get('board_id', '')
  search_author_id = request.GET.get('author_id', '')
  search_category_id = request.GET.get('category_id', '')
  search_address = request.GET.get('address', '')
  place_status = request.GET.get('place_status', '')

  # status
  all_post = models.POST.objects.prefetch_related('boards').select_related('author', 'place_info', 'related_post').prefetch_related('place_info__categories').all()

  # 게시글 검색
  sps = all_post.filter(
    Q(place_info__isnull=False), # 여행지 정보가 있는 게시글만 검색
    Q(title__contains=search_post_title),
    Q(author__username__contains=search_author_id),
    Q(place_info__categories__id__contains=search_category_id),
    Q(place_info__address__contains=search_address),
    Q(place_info__status__contains=place_status),
  )

  if search_board_id: # 게시판 필터링
    sps = sps.filter(boards__id__contains=search_board_id)

  # export
  if request.GET.get('export'):
    headers = ['id', 'title', 'image', 'view_count', 'like_count', 'created_at', 'search_weight', 'board', 'author', 'place_info', 'related_post']
    values = [
        [str(post.id) for post in sps],
        [post.title for post in sps],
        [str(post.image) for post in sps],
        [str(post.view_count) for post in sps],
        [str(post.like_count) for post in sps],
        [str(post.created_at) for post in sps],
        [str(post.search_weight) for post in sps],
        [str(post.boards.all().last().name) for post in sps],
        [str(post.author.username) for post in sps],
        [str(post.place_info) for post in sps],
        [str(post.related_post) for post in sps],
    ]

    # 행(row) 중심 데이터 변환 (Transpose)
    table_data = list(zip(*values))

    return render(request, 'export.html', {
        **daos.get_urls(),
        'headers': headers,
        'table_data': table_data,
    })

  last_page = sps.count() // 20 + 1 # 20개씩 표시
  search_posts = []
  for post in sps[(page - 1) * 20:page * 20]:
    try:
      search_posts.append({
        'id': post.id,
        'title': post.title,
        'image': '/media/' + str(post.image) if post.image else None,
        'view_count': post.view_count,
        'like_count': post.like_count,
        'created_at': datetime.datetime.strftime(post.created_at, '%Y-%m-%d'),
        'search_weight': post.search_weight,
        'board': {
          'name': post.boards.all().last().name,
          'board_type': post.boards.all().last().board_type,
        },
        'author': {
          'id': post.author.username, # 작성자 아이디
          'nickname': post.author.first_name, # 작성자 닉네임
          'partner_name': post.author.last_name, # 작성자 파트너 이름
        },
        'place_info': { # 여행지 게시글인 경우, 여행지 정보
          'categories': [{
            'id': c.id,
            'name': c.name,
          } for c in post.place_info.categories.all()],
          'address': post.place_info.address,
          'location_info': post.place_info.location_info,
          'open_info': post.place_info.open_info,
          'ad_start_at': datetime.datetime.strftime(post.place_info.ad_start_at, '%Y-%m-%d'),
          'ad_end_at': datetime.datetime.strftime(post.place_info.ad_end_at, '%Y-%m-%d'),
          'status': post.place_info.status,
          'note': post.place_info.note,
        } if post.place_info else None,
      })
    except Exception as e:
      print(e)

  # 카테고리 정보
  boards = daos.make_travel_board_tree()
  categories = daos.make_category_tree()

  return render(request, 'supervisor/travel.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'posts': search_posts, # 검색된 게시글 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
    'status': boards, # 게시판 별 통계 데이터. 게시판 별로 게시글 수, 댓글 수, 조회수, 좋아요 수 제공
    'boards': boards, # 게시판 정보
    'categories': categories, # 카테고리 정보
  })

# 여행지 게시글 수정
def travel_edit(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if 'post' not in account['subsupervisor_permissions']:
    return redirect('/')

  # 여행지 게시글 수정
  if request.method == 'POST':
    daos.update_post(
      post_id=request.GET['post_id'],
      board_ids=request.POST.get('board_ids'),
      title=request.POST.get('title'),
      content=request.POST.get('content'),
      image=request.FILES.get('image', None),
      search_weight=request.POST.get('search_weight'),
      view_count=request.POST.get('view_count'),
      like_count=request.POST.get('like_count'),
    )
    daos.update_place_info(
      post_id=request.GET['post_id'],
      category_ids=request.POST.get('category_ids'),
      location_info=request.POST.get('location_info'),
      open_info=request.POST.get('open_info'),
      address=request.POST.get('address'),
    )
    return JsonResponse({'result': 'success'})

  # 여행지 게시글 삭제
  if request.method == 'DELETE':
    post_id = request.GET.get('post_id', None)
    post = daos.select_post(post_id)
    daos.delete_place_info(post['place_info']['id'])
    return JsonResponse({
      'result': 'success',
    })

  # data
  post_id = request.GET.get('post_id', '')
  post = daos.select_post(post_id)
  categories = daos.make_category_tree()
  boards = daos.make_travel_board_tree()

  return render(request, 'supervisor/travel_edit.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,
    'post': post,
    'categories': categories,
    'boards': boards,
  })

# 쿠폰 관리 페이지
def coupon(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if 'coupon' not in account['subsupervisor_permissions']:
    return redirect('/')

  # data
  tab_type = request.GET.get('tab', 'couponTab') # coupon, history
  page = int(request.GET.get('page', '1'))
  search_coupon_code = request.GET.get('coupon_code', '')
  search_coupon_name = request.GET.get('coupon_name', '')

  # status
  status = {
    'active': models.COUPON.objects.filter(status='active').count(),
    'expired': models.COUPON.objects.filter(status='expired').count(),
    'deleted': models.COUPON.objects.filter(status='deleted').count(),
  }

  # 쿠폰 검색
  if tab_type == 'couponTab':
    cs = models.COUPON.objects.select_related('related_post', 'create_account').prefetch_related('own_accounts').filter(
      Q(status='active')
    ).filter(
      code__contains=search_coupon_code,
      name__contains=search_coupon_name,
    ).order_by('-created_at')
  elif tab_type == 'historyTab':
    cs = models.COUPON.objects.select_related('related_post', 'create_account').prefetch_related('own_accounts').exclude(
      Q(status='active')
    ).filter(
      code__contains=search_coupon_code,
      name__contains=search_coupon_name,
    ).order_by('-created_at')

  if request.GET.get('export'):
    headers = ['code', 'name', 'image', 'content', 'required_mileage', 'expire_at', 'status', 'post', 'create_account']
    values = [
        [coupon.code for coupon in cs],
        [coupon.name for coupon in cs],
        [str(coupon.image) for coupon in cs],
        [coupon.content for coupon in cs],
        [coupon.required_mileage for coupon in cs],
        [coupon.expire_at for coupon in cs],
        [coupon.status for coupon in cs],
        [coupon.related_post.title for coupon in cs],
        [coupon.create_account.last_name for coupon in cs],
    ]

    # 행(row) 중심 데이터 변환 (Transpose)
    table_data = list(zip(*values))

    return render(request, 'export.html', {
        **daos.get_urls(),
        'headers': headers,
        'table_data': table_data,
    })

  last_page = cs.count() // 20 + 1 # 20개씩 표시
  coupons = []
  for coupon in cs[(page - 1) * 20:page * 20]:
    coupons.append({
      'code': coupon.code,
      'name': coupon.name,
      'image': '/media/' + str(coupon.image) if coupon.image else None,
      'content': coupon.content,
      'required_mileage': coupon.required_mileage,
      'expire_at': datetime.datetime.strftime(coupon.expire_at, '%Y-%m-%d'),
      'status': coupon.status,
      'post': {
        'id': coupon.related_post.id,
        'title': coupon.related_post.title,
      },
      'create_account': {
        'id': coupon.create_account.username,
        'partner_name': coupon.create_account.last_name,
      },
    })

  return render(request, 'supervisor/coupon.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'status': status, # 쿠폰 종류(탭) 별 통계 데이터
    'coupons': coupons, # 검색된 쿠폰 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
  })

# 쪽지 관리 페이지
def message(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if 'message' not in account['subsupervisor_permissions']:
    return redirect('/')

  # data
  tab = request.GET.get('tab', 'inboxTab') # inbox, outbox
  page = int(request.GET.get('page', '1'))
  search_message_title = request.GET.get('message_title', '')
  search_message_receiver = request.GET.get('message_receiver', '')

  # status
  status = {
    'unread': models.MESSAGE.objects.filter(is_read=False, to_account='supervisor').count(),
    'read': models.MESSAGE.objects.filter(is_read=True, to_account='supervisor').count(),
  }

  # 받은 쪽지함
  if tab == 'inboxTab':
    msgs = models.MESSAGE.objects.select_related('include_coupon').filter(
      to_account='supervisor',
      title__contains=search_message_title,
      sender_account__contains=search_message_receiver,
    ).order_by('-created_at')

    # export
    if request.GET.get('export'):
      headers = ['id', 'title', 'content', 'is_read', 'created_at', 'sender']
      values = [
        [m.id for m in msgs],
        [m.title for m in msgs],
        [m.content for m in msgs],
        [m.is_read for m in msgs],
        [m.created_at for m in msgs],
        [m.sender_account for m in msgs],
      ]

      # 행(row) 중심 데이터 변환 (Transpose)
      table_data = list(zip(*values))

      return render(request, 'export.html', {
        **daos.get_urls(),
        'headers': headers,
        'table_data': table_data
      })

    last_page = len(msgs) // 20 + 1
    messages = [{
      'id': m.id,
      'title': m.title,
      'content': m.content,
      'is_read': m.is_read,
      'created_at': m.created_at,
      'image': '/media/' + str(m.image) if m.image else None,
      'include_coupon': {
        'code': m.include_coupon.code,
        'name': m.include_coupon.name,
      } if m.include_coupon else None,
      'sender': {
        'id': sd.username,
        'nickname': sd.first_name,
        'partner_name': sd.last_name,
        'level': {
          'level': sd.level.level,
          'image': '/media/' + str(sd.level.image) if sd.level.image else None,
          'text': sd.level.text,
          'text_color': sd.level.text_color,
          'background_color': sd.level.background_color,
        } if sd.level else None,
        'groups': [g.name for g in sd.groups.all()],
      } if (sd := models.ACCOUNT.objects.prefetch_related('groups').select_related('level').filter(username=m.sender_account).first()) else {'id': m.sender_account},
    } for m in msgs[(page - 1) * 20:page * 20]]

    return render(request, 'supervisor/message.html', {
      **daos.get_urls(),
      'account': account,
      'server_settings': server_settings,

      'status': status,
      'messages': messages,
      'last_page': last_page,
    })

  elif tab == 'outboxTab': # 보낸 쪽지함
    msgs = models.MESSAGE.objects.select_related('include_coupon').filter(
      sender_account='supervisor',
      title__contains=search_message_title,
      to_account__contains=search_message_receiver,
    ).order_by('-created_at')

    # export
    if request.GET.get('export'):
      headers = ['id', 'title', 'content', 'is_read', 'created_at', 'to']
      values = [
        [m.id for m in msgs],
        [m.title for m in msgs],
        [m.content for m in msgs],
        [m.is_read for m in msgs],
        [m.created_at for m in msgs],
        [m.to_account for m in msgs],
      ]

      # 행(row) 중심 데이터 변환 (Transpose)
      table_data = list(zip(*values))

      return render(request, 'export.html', {
        **daos.get_urls(),
        'headers': headers,
        'table_data': table_data
      })

    last_page = len(msgs) // 20 + 1
    messages = [{
      'id': m.id,
      'title': m.title,
      'content': m.content,
      'is_read': m.is_read,
      'created_at': m.created_at,
      'image': '/media/' + str(m.image) if m.image else None,
      'include_coupon': {
        'code': m.include_coupon.code,
        'name': m.include_coupon.name,
      } if m.include_coupon else None,
      'to': {
        'id': rc.username,
        'nickname': rc.first_name,
        'partner_name': rc.last_name,
        'level': {
          'level': rc.level.level,
          'image': '/media/' + str(rc.level.image) if rc.level.image else None,
          'text': rc.level.text,
          'text_color': rc.level.text_color,
          'background_color': rc.level.background_color,
        } if rc.level else None,
        'groups': [g.name for g in rc.groups.all()],
      } if (rc := get_user_model().objects.prefetch_related('groups').select_related('level').get(username=m.to_account)) else {'id': m.to_account},
    } for m in msgs[(page - 1) * 20:page * 20]]

    return render(request, 'supervisor/message.html', {
      **daos.get_urls(),
      'account': account,
      'server_settings': server_settings,

      'status': status,
      'messages': messages,
      'last_page': last_page,
    })

# 배너 관리 페이지
def banner(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if 'banner' not in account['subsupervisor_permissions']:
    return redirect('/')

  # 배너 생성 및 수정 요청 처리
  # 아이디가 있으면 수정, 없으면 생성
  if request.method == 'POST':
    id = request.GET.get('id')
    if id:
      daos.update_banner(
        banner_id=id,
        image=request.FILES.get('image', None),
        link=request.POST.get('link', ''),
        display_weight=request.POST.get('display_weight', ''),
        location=request.POST.get('location', ''),
        size=request.POST.get('size', ''),
      )
    else:
      daos.create_banner(
        image=request.FILES.get('image', None),
        link=request.POST.get('link', ''),
        display_weight=request.POST.get('display_weight', ''),
        location=request.POST.get('location', ''),
        size=request.POST.get('size', ''),
      )
    return JsonResponse({'result': 'success'})

  # 배너 삭제
  if request.method == 'DELETE':
    banner_id = request.GET.get('id', '')
    daos.delete_banner(banner_id)
    return JsonResponse({'result': 'success'})

  # data
  tab = request.GET.get('tab', 'topTab') # top, side

  # search
  banners = []
  for b in models.BANNER.objects.all().order_by('-display_weight'):
    if b.location == 'side' and tab == 'sideTab':
      banners.append({
        'id': b.id,
        'location': b.location,
        'image': '/media/' + str(b.image) if b.image else None,
        'link': b.link,
        'display_weight': b.display_weight,
        'size': 'full',
      })
    elif b.location == 'top' and tab == 'topTab':
      banners.append({
        'id': b.id,
        'location': b.location,
        'image': '/media/' + str(b.image) if b.image else None,
        'link': b.link,
        'display_weight': b.display_weight,
        'size': b.size,
      })

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
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if 'level' not in account['subsupervisor_permissions']:
    return redirect('/')

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

  lvs = models.LEVEL_RULE.objects.all().order_by('level')
  levels = [{
    'level': lv.level,
    'image': '/media/' + str(lv.image) if lv.image else None,
    'text': lv.text,
    'text_color': lv.text_color,
    'background_color': lv.background_color,
    'required_exp': lv.required_exp,
  } for lv in lvs]

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
    return redirect('/')
  else:
    account = daos.select_account_detail(request.user.id)
    server_settings = {
        'site_logo': daos.select_server_setting('site_logo'),
        'service_name': daos.select_server_setting('service_name'),
    }
  if 'setting' not in account['subsupervisor_permissions']:
    return redirect('/')

  # 설정 정보 변경 요청 처리
  if request.method == 'POST':
    print(request.POST.dict())
    daos.update_server_setting('service_name', request.POST.get('service_name'))
    daos.update_server_setting('site_logo', request.POST.get('site_logo'))
    daos.update_server_setting('site_header', request.POST.get('site_header'))
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
      'site_header': daos.select_server_setting('site_header'),
      'company_info': daos.select_server_setting('company_info'),
      'terms': daos.select_server_setting('terms'),
      'register_point': daos.select_server_setting('register_point'),
      'attend_point': daos.select_server_setting('attend_point'),
      'post_point': daos.select_server_setting('post_point'),
      'review_point': daos.select_server_setting('review_point'),
      'comment_point': daos.select_server_setting('comment_point'),
    },
  })