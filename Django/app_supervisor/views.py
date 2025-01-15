import datetime
import math
import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, get_user_model
from django.db.models import Q

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
# server, account, messages
def get_default_context(request):

  # 사용자 프로필 정보 가져오기
  # 로그인하지 않은 사용자는 guest로 처리
  account = user_do.get_user_profile(request)

  # 읽지 않는 쪽지 미리보기
  # 관리자의 경우 수신자가 'supervisor'인 쪽지로 검색해서 가져옴
  messages = message_do.get_user_message_previews(request)

  # 서버 설정 가져오기
  server = core_do.get_server_settings()

  return {
    'server': server,
    'messages': messages,
    'account': account,
  }

# 관리자 메인 페이지
def index(request):
  context = get_default_context(request)
  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if 'supervisor' not in context['account']['account_type']:
    return redirect('/?redirect=permission_denied')

  # TODO: 현재 관리자 메인 페이지에 별도의 요소가 없음.. 디자이너와 상의 후 추가할 수 있음

  return render(request, 'supervisor/index.html', context)

# 계정 관리 페이지
# 계정별 마지막 로그인 시간 및 회원가입일, 관리자 노트 등 포함
# 관리자 생성 및 사용자 정보 수정 기능 포함(삭제도 사용자 정보 수정으로 가능)
def account(request):
  context = get_default_context(request)
  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if 'supervisor' not in context['account']['account_type']:
    return redirect('/?redirect=permission_denied')

  # 관리자 신규 생성 처리
  # method='POST', action='create_supervisor'일 경우, 관리자 계정 생성 요청으로 처리
  if request.method == 'POST' and request.POST.get('action') == 'create_supervisor':
    id = request.POST['id']
    password = request.POST['password']
    permissions = request.POST.get('permissions', '')
    account = get_user_model().objects.create_user(
      username = id,
      first_name = '관리자',
      account_type = 'sub_supervisor',
      supervisor_permissions = permissions,
    )
    account.set_password(password)
    account.save()
    return JsonResponse({'result': 'success'})

  # 계정 정보 수정 요청 처리(삭제도 포함) 삭제는 status를 deleted로 변경
  # method='POST', action='update_account'일 경우, 계정 정보 수정 요청으로 처리
  # 비밀번호, 닉네임, 계정 상태, 쿠폰 포인트, 레벨업 포인트, 관리자 권한 수정 가능
  if request.method == 'POST' and request.POST.get('action') == 'update_account':
    id = request.POST['id']
    acnt = get_user_model().objects.get(username=id)
    acnt.status = request.POST.get('status', acnt.status)
    new_password = request.POST.get('password', '')
    if new_password != '':
      acnt.set_password(new_password)
    acnt.first_name = request.POST.get('nickname', acnt.first_name)
    acnt.user_level_point = request.POST.get('levelPoint', acnt.user_level_point)
    acnt.user_usable_point = request.POST.get('usablePoint', acnt.user_usable_point)
    acnt.super_permissions = request.POST.get('permissions', acnt.super_permissions)
    acnt.save()

    return JsonResponse({'result': 'success'})

  # data
  tab = request.GET.get('tab', 'user')
  page = int(request.GET.get('page', '1'))
  search_account_id = request.GET.get('accountId', '')
  search_account_nickname = request.GET.get('accountNickname', '')
  search_account_status = request.GET.get('accountStatus', '')

  # 계정 타입별로 계정 통계 가져오기
  # 관리자 계정 탭은 별도의 통계 없음.
  # 파트너는 각 카테고리면 파트너 계정 통계 제공
  # 사용자는 사용자 및 여성 회원의 계정 통계 제공
  all_accounts = get_user_model().objects.all().order_by('-date_joined')
  if tab == 'supervisor': # 관리자 검색 탬일 경우, 별도의 사용자 통계 기능 없음.
    status = {}
  elif tab == 'user': # 사용자 검색 탭일 경우, 사용자 및 여성회원 정보 제공
    dame_accounts = all_accounts.filter(
      account_type = 'dame'
    )
    user_accounts = all_accounts.filter(
      account_type = 'user'
    )
    status = {
      'user': {
        'active': user_accounts.filter(status='active').count(),
        'pending': user_accounts.filter(status='pending').count(),
        'sleeping': user_accounts.filter(status='sleeping').count(),
        'deleted': user_accounts.filter(status='deleted').count(),
        'blocked': user_accounts.filter(status='blocked').count(),
        'banned': user_accounts.filter(status='banned').count(),
      },
      'dame': {
        'active': dame_accounts.filter(status='active').count(),
        'pending': dame_accounts.filter(status='pending').count(),
        'sleeping': dame_accounts.filter(status='sleeping').count(),
        'deleted': dame_accounts.filter(status='deleted').count(),
        'blocked': dame_accounts.filter(status='blocked').count(),
        'banned': dame_accounts.filter(status='banned').count(),
      }
    }
  elif tab == 'partner': # 파트너 검색 탭일 경우, 파트너 정보 제공
    # 파트너 계정은 각 카테고리별 계정 상태 현황 제공
    categories = partner_mo.CATEGORY.objects.all()
    category_dict = {
      category.name: {
        'id': category.id,
        'name': category.name,
        'active': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='active').count(),
        'pending': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='pending').count(),
        'sleeping': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='sleeping').count(),
        'deleted': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='deleted').count(),
        'blocked': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='blocked').count(),
        'banned': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='banned').count(),
        'children': [],
      } for category in categories if category.parent_id == ''
    }
    for category in categories:
      if category.parent_id:
        if category_dict.get(partner_mo.CATEGORY.objects.get(id=category.parent_id).name):
          category_dict[partner_mo.CATEGORY.objects.get(id=category.parent_id).name]['children'].append({
            'id': category.id,
            'name': category.name,
            'active': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='active').count(),
            'pending': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='pending').count(),
            'sleeping': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='sleeping').count(),
            'deleted': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='deleted').count(),
            'blocked': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='blocked').count(),
            'banned': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='banned').count(),
            'children': [],
          })
        else:
          loop = True
          for key in category_dict.keys():
            for child in category_dict[key]['children']:
              # 3단계 카테고리
              if not loop:
                break
              if str(child['id']) == str(category.parent_id):
                child['children'].append({
                  'id': category.id,
                  'name': category.name,
                  'active': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='active').count(),
                  'pending': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='pending').count(),
                  'sleeping': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='sleeping').count(),
                  'deleted': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='deleted').count(),
                  'blocked': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='blocked').count(),
                  'banned': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='banned').count(),
                  'children': [],
                })
                loop = False
              # 4단계 카테고리
              if loop:
                for grandchild in child['children']:
                  if not loop:
                    break
                  if str(grandchild['id']) == str(category.parent_id):
                    grandchild['children'].append({
                      'id': category.id,
                      'name': category.name,
                      'active': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='active').count(),
                      'pending': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='pending').count(),
                      'sleeping': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='sleeping').count(),
                      'deleted': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='deleted').count(),
                      'blocked': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='blocked').count(),
                      'banned': all_accounts.filter(partner_categories__contains=category.name, account_type='partner', status='banned').count(),
                      'children': [],
                    })
                    loop = False
    status = {
      'partner': []
    }
    for child in category_dict.keys():
      status['partner'].append(category_dict[child])

  # 사용자 검색
  if tab == 'user': # 사용자 탭일 경우, user와 dame을 같이 검색
    sats = all_accounts.filter(
      Q(account_type='user') | Q(account_type='dame'), # 사용자 및 여성회원
      Q(username__contains=search_account_id) | Q(first_name__contains=search_account_nickname) | Q(status__contains=search_account_status)
    )
  else: # 그외(파트너 및 관리자 탭)
    sats = all_accounts.filter(
      Q(account_type__contains=tab),
      Q(username__contains=search_account_id) | Q(first_name__contains=search_account_nickname) | Q(status__contains=search_account_status)
    )
  last_page = sats.count() // 20 + 1 # 20개씩 표시
  search_accounts = []
  for account in sats[(page - 1) * 20:page * 20]:

    # 사용자 레벨 정보(사용자만)
    if account.account_type == 'user' or account.account_type == 'dame':
      lv = core_mo.LEVEL_RULE.objects.get(level=account.user_level)
      level = {
        'level': account.user_level,
        'text_color': lv.text_color,
        'background_color': lv.background_color,
        'name': lv.name,
      }
    else:
      level = None

    search_accounts.append({
      'id': account.username,
      'nickname': account.first_name,
      'account_type': account.account_type,
      'status': account.status,
      'date_joined': account.date_joined,
      'last_login': account.last_login,
      'note': account.note,
      'user_usable_point': account.user_usable_point,
      'user_level_point': account.user_level_point,
      'user_level': level,
      'partner_tel': account.partner_tel,
      'partner_address': account.partner_address,
      'partner_categories': account.partner_categories,
      'supervisor_permissions': account.supervisor_permissions,
    })

  return render(request, 'supervisor/account.html', {
    **context,
    'search_accounts': search_accounts, # 검색된 계정 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
    'status': status, # 사용자 종류(탭) 별 통계 데이터(관리자는 없음)
  })

# 게시글 관리 페이지
def post(request):
  context = get_default_context(request)
  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if 'supervisor' not in context['account']['account_type']:
    return redirect('/?redirect=permission_denied')

  # post_id 게시글 강제 삭제
  if request.method == 'DELETE':
    post_id = request.GET.get('post_id', '')

    # 댓글 삭제
    post_mo.COMMENT.objects.filter(post_id=post_id).delete()

    # 게시글 확인
    po = post_mo.POST.objects.get(id=post_id)

    # 게시글 작성자 포인트 회수
    author = get_user_model().objects.get(username=po.author_id)
    author.user_usable_point -= int(core_mo.SERVER_SETTING.objects.get(id='post_point').value)
    if author.user_usable_point < 0:
      author.user_usable_point = 0
    author.save()

    # 게시글 작성자에게 활동 기록 생성
    act = user_mo.ACTIVITY(
      message = f'[관리자] {po.title} 게시글이 관리자에 의해 삭제되었습니다.',
      user_id = po.author_id,
      point_change = f'-{core_mo.SERVER_SETTING.objects.get(id="post_point").value}',
    )
    act.save()

    # 게시글 삭제
    po.delete()

    return JsonResponse({'result': 'success'})

  # data
  page = int(request.GET.get('page', '1'))
  search_post_title = request.GET.get('postTItle', '')
  search_board_id = request.GET.get('boardId', '')

  # status
  # 각 게시판 별 게시글 수와 댓글 수, 조회수, 좋아요 수 통계 제공
  all_posts = post_mo.POST.objects.all().order_by('-created_dt')
  boards = post_mo.BOARD.objects.exclude(
    Q(post_type='attendance') | Q(post_type='greeting')
  )
  board_dict = {
    board.name: {
      'id': board.id,
      'name': board.name,
      'post_type': board.post_type,
      'total_views': int(math.fsum([len(str(post.views).split(',')) - 1 for post in post_mo.POST.objects.filter(Q(board_id__contains=board.id))])),
      'total_comments': post_mo.COMMENT.objects.filter(post_id__in=[post.id for post in post_mo.POST.objects.filter(Q(board_id__contains=board.id))]).count(),
      'total_posts': post_mo.POST.objects.filter(Q(board_id__contains=board.id)).count(),
      'display_permissions': str(board.display_permissions),
      'enter_permissions': str(board.enter_permissions),
      'write_permissions': str(board.write_permissions),
      'comment_permissions': str(board.comment_permissions),
      'children': [],
    } for board in boards if board.parent_id == ''
  }
  for board in boards:
    if board.parent_id:
      if board_dict.get(post_mo.BOARD.objects.get(id=board.parent_id).name):
        board_dict[post_mo.BOARD.objects.get(id=board.parent_id).name]['children'].append({
          'id': board.id,
          'name': board.name,
          'post_type': board.post_type,
          'total_views': int(math.fsum([len(str(post.views).split(',')) - 1 for post in post_mo.POST.objects.filter(Q(board_id__contains=board.id))])),
          'total_comments': post_mo.COMMENT.objects.filter(post_id__in=[post.id for post in post_mo.POST.objects.filter(Q(board_id__contains=board.id))]).count(),
          'total_posts': post_mo.POST.objects.filter(Q(board_id__contains=board.id)).count(),
          'display_permissions': str(board.display_permissions),
          'enter_permissions': str(board.enter_permissions),
          'write_permissions': str(board.write_permissions),
          'comment_permissions': str(board.comment_permissions),
          'children': [],
        })
      else:
        loop = True
        for key in board_dict.keys():
          for child in board_dict[key]['children']:
            # 3단계 게시판
            if not loop:
              break
            if str(child['id']) == str(board.parent_id):
              child['children'].append({
                'id': board.id,
                'name': board.name,
                'post_type': board.post_type,
                'total_views': int(math.fsum([len(str(post.views).split(',')) - 1 for post in post_mo.POST.objects.filter(Q(board_id__contains=board.id))])),
                'total_comments': post_mo.COMMENT.objects.filter(post_id__in=[post.id for post in post_mo.POST.objects.filter(Q(board_id__contains=board.id))]).count(),
                'total_posts': post_mo.POST.objects.filter(Q(board_id__contains=board.id)).count(),
                'display_permissions': str(board.display_permissions),
                'enter_permissions': str(board.enter_permissions),
                'write_permissions': str(board.write_permissions),
                'comment_permissions': str(board.comment_permissions),
                'children': [],
              })
              loop = False
            # 4단계 게시판
            if loop:
              for grandchild in child['children']:
                if not loop:
                  break
                if str(grandchild['id']) == str(board.parent_id):
                  grandchild['children'].append({
                    'id': board.id,
                    'name': board.name,
                    'post_type': board.post_type,
                    'total_views': int(math.fsum([len(str(post.views).split(',')) - 1 for post in post_mo.POST.objects.filter(Q(board_id__contains=board.id))])),
                    'total_comments': post_mo.COMMENT.objects.filter(post_id__in=[post.id for post in post_mo.POST.objects.filter(Q(board_id__contains=board.id))]).count(),
                    'total_posts': post_mo.POST.objects.filter(Q(board_id__contains=board.id)).count(),
                    'display_permissions': str(board.display_permissions),
                    'enter_permissions': str(board.enter_permissions),
                    'write_permissions': str(board.write_permissions),
                    'comment_permissions': str(board.comment_permissions),
                    'children': [],
                  })
                  loop = False
  status = []
  for child in board_dict.keys():
    status.append(board_dict[child])

  # 게시글 검색
  sps = all_posts.filter(
    Q(title__contains=search_post_title),
    Q(board_id__contains=search_board_id)
  )
  last_page = sps.count() // 20 + 1 # 20개씩 표시
  search_posts = []
  for post in sps[(page - 1) * 20:page * 20]:

    # 게시글 작성자 정보
    at = get_user_model().objects.filter(username=post.author_id).first()
    if not at:
      continue
    author = {
      'id': post.author_id,
      'nickname': at.first_name,
      'account_type': at.account_type,
      'status': at.status,
    }

    # 게시글이 속한 게시판 정보
    boards = []
    for b in str(post.board_id).split(','):
      if b == '':
        continue
      board = post_mo.BOARD.objects.get(id=b)
      boards.append({
        'id': board.id,
        'name': board.name,
      })

    # 게시글 정보
    search_posts.append({
      'id': post.id,
      'title': post.title,
      'boards': boards,
      'author': author,
      'created_dt': post.created_dt,
      'view_count': len(str(post.views).split(',')) - 1,
      'like_count': len(str(post.bookmarks).split(',')) - 1,
      'comment_count': post_mo.COMMENT.objects.filter(post_id=post.id).count(),
    })

  return render(request, 'supervisor/post.html', {
    **context,
    'search_posts': search_posts, # 검색된 게시글 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
    'status': status, # 게시판 별 통계 데이터. 게시판 별로 게시글 수, 댓글 수, 조회수, 좋아요 수 제공
  })

# 광고 게시글 관리 페이지
def ad_post(request):
  context = get_default_context(request)
  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if 'supervisor' not in context['account']['account_type']:
    return redirect('/?redirect=permission_denied')

  # 광고 정책 수정 요청 처리
  # 광고 게시글은 파트너가 생성하므로 삭제 또는 생성 불가. 수정만 가능
  if request.method == 'PATCH':
    update_ad_id = request.GET.get('ad_id', '')
    ad = post_mo.AD.objects.get(id=update_ad_id)
    ad.weight = request.GET.get('ad_weight', ad.weight)
    ad.note = request.GET.get('ad_note', ad.note)
    ad.start_dt = request.GET.get('ad_start_dt', ad.start_dt)
    ad.end_dt = request.GET.get('ad_end_dt', ad.end_dt)
    ad.save()
    return JsonResponse({'result': 'success'})

  # data
  page = int(request.GET.get('page', '1'))
  search_post_title = request.GET.get('postTItle', '')
  search_ad_status = request.GET.get('adStatus', '')

  # status
  # 광고 게시글 통계 정보 제공
  # 광고 상태별 통계 제공(활성, 만료). 활성 상태인 경우, 베시트 업체 뱃지가 표시됨
  all_ads = post_mo.AD.objects.all().order_by('status', '-end_dt', '-weight')
  status = {
    'active': all_ads.filter(status='active').count(),
    'expired': all_ads.filter(status='expired').count(),
  }

  # search
  sas = all_ads.filter(
    Q(status__contains=search_ad_status),
  )
  last_page = sas.count() // 20 + 1 # 20개씩 표시
  search_ads = []
  for ad in sas[(page - 1) * 20:page * 20]:

    # 광고 게시글 정보
    post = post_mo.POST.objects.filter(
      Q(title__contains=search_post_title),
      id = ad.post_id,
    ).first()
    if not post:
      continue

    # 광고 게시글 작성자 정보
    at = get_user_model().objects.get(username=post.author_id)
    author = {
      'id': post.author_id,
      'nickname': at.first_name,
      'partner_categories': at.partner_categories,
      'partner_address': at.partner_address,
      'partner_tel': at.partner_tel,
    }

    # 광고 게시글이 속한 게시판 정보
    boards = []
    for b in str(post.board_id).split(','):
      if b == '':
        continue
      board = post_mo.BOARD.objects.get(id=b)
      boards.append({
        'id': board.id,
        'name': board.name,
      })

    # 광고 게시글 정보
    post = {
      'id': post.id,
      'status': ad.status,
      'title': post.title,
      'boards': boards,
      'author': author,
      'created_dt': post.created_dt,
      'view_count': len(str(post.views).split(',')) - 1,
      'bookmark_count': len(str(post.bookmarks).split(',')) - 1,
      'image': str(post.images).split(',')[0],
      'comment_count': post_mo.COMMENT.objects.filter(post_id=post.id).count
    }

    # 광고 정보
    search_ads.append({
      'id': ad.id,
      'post': post,
      'start_dt': ad.start_dt,
      'end_dt': ad.end_dt,
      'status': ad.status,
      'weight': ad.weight, # 광고 게시글의 가중치. 이 필드로 우선 순위가 결정됨
      'note': ad.note,
    })

  return render(request, 'supervisor/ad_post.html', {
    **context,
    'search_ads': search_ads, # 검색된 광고 게시글 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
    'status': status, # 광고 상태별 통계 데이터 제공
  })

# 쿠폰 관리 페이지
# 별도의 쿠폰 수정 삭제 기능은 없음
def coupon(request):
  context = get_default_context(request)
  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if 'supervisor' not in context['account']['account_type']:
    return redirect('/?redirect=permission_denied')

  # data
  tab_type = request.GET.get('tab', 'coupon')
  page = int(request.GET.get('page', '1'))
  search_coupon_name = request.GET.get('couponName', '')
  coupon_status = request.GET.get('couponStatus', 'used')

  # status
  if tab_type == 'coupon':
    all_coupons = coupon_mo.COUPON.objects.all().order_by('-created_dt')
    status = {
      'coupon': all_coupons.count(),
    }

    # search
    scs = all_coupons.filter(
      name__contains=search_coupon_name # 쿠폰 이름 검색
    )
    last_page = scs.count() // 20 + 1 # 20개씩 표시
    search_coupons = []
    for coupon in scs[(page - 1) * 20:page * 20]: # 페이지 처리

      # 쿠폰이 속한 게시글 정보
      coupon_po = post_mo.POST.objects.filter(id=coupon.post_id).first()
      if not coupon_po:
        continue
      coupon_po_at = get_user_model().objects.filter(username=coupon_po.author_id).first()
      author = {
        'id': coupon_po.author_id,
        'nickname': coupon_po_at.first_name,
        'partner_categories': coupon_po_at.partner_categories,
        'partner_address': coupon_po_at.partner_address,
      }
      post = {
        'id': coupon_po.id,
        'title': coupon_po.title,
        'author': author,
      }

      # create account
      create_account = get_user_model().objects.filter(username=coupon.create_account_id).first()

      search_coupons.append({
        'id': coupon.id,
        'code': coupon.code,
        'name': coupon.name,
        'description': coupon.description,
        'create_account': {
          'nickname': create_account.first_name,
        },
        'images': str(coupon.images).split(','),
        'post': post,
        'created_dt': coupon.created_dt,
        'required_point': coupon.required_point,
      })

    return render(request, 'supervisor/coupon.html', {
      **context,
      'coupons': search_coupons,
      'last_page': last_page,
      'status': status,
    })

  else:
    all_history = coupon_mo.COUPON_HISTORY.objects.all().order_by('-created_dt')
    status = {
      'history': {
        'used': all_history.filter(status='used').count(),
        'expired': all_history.filter(status='expired').count(),
        'deleted': all_history.filter(status='deleted').count(),
      }
    }

    # search
    shs = all_history.filter(
      name__contains=search_coupon_name,
    )
    last_page = shs.count() // 20 + 1 # 20개씩 표시
    search_histories = []
    for history in shs[(page - 1) * 20:page * 20]:

      # 쿠폰이 속한 게시글 정보
      coupon_po = post_mo.POST.objects.filter(id=history.post_id).first()
      coupon_po_at = get_user_model().objects.filter(username=coupon_po.author_id).first()
      author = {
        'id': coupon_po.author_id,
        'nickname': coupon_po_at.first_name,
        'partner_categories': coupon_po_at.partner_categories,
        'partner_address': coupon_po_at.partner_address,
      }
      post = {
        'id': coupon_po.id,
        'title': coupon_po.title,
        'author': author,
      }

      search_histories.append({
        'id': history.id,
        'code': history.code,
        'name': history.name,
        'description': history.description,
        'images': str(history.images).split(','),
        'post': post,
        'created_dt': history.created_dt,
        'used_dt': history.used_dt,
        'required_point': history.required_point,
        'status': history.status,
        'note': history.note,
      })

    return render(request, 'supervisor/coupon.html', {
      **context,
      'histories': search_histories,
      'last_page': last_page,
      'status': status,
    })

# 쪽지 관리 페이지
def message(request):
  context = get_default_context(request)
  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if 'supervisor' not in context['account']['account_type']:
    return redirect('/?redirect=permission_denied')

  # data
  tab = request.GET.get('tab', 'inbox')
  page = int(request.GET.get('page', '1'))
  search_message_title = request.GET.get('messageTitle', '')
  search_message_receiver = request.GET.get('messageReceiver', '')

  # 받은 쪽지함
  if tab == 'inbox':
    all_messages = message_mo.MESSAGE.objects.filter(receiver_id='supervisor').order_by('-send_dt')
    status = {
      'inbox': {
        'count': all_messages.count(),
        'unread': all_messages.filter(read_dt=None).count(),
      }
    }

    # search
    sms = all_messages.filter(
      title__contains=search_message_title,
      sender_id__contains=search_message_receiver
    )
    last_page = sms.count() // 20 + 1 # 20개씩 표시
    search_messages = []
    for message in sms[(page - 1) * 20:page * 20]:

      # 쪽지 발신자
      sd = get_user_model().objects.filter(username=message.sender_id).first()
      if not sd:
        sender = {
          'id': message.sender_id,
          'nickname': '게스트',
          'account_type': 'guest',
          'status': 'active',
        }
      else:
        if sd.account_type == 'partner':
          sender = {
            'id': message.sender_id,
            'nickname': sd.first_name,
            'account_type': sd.account_type,
            'status': sd.status,
            'partner_categories': sd.partner_categories,
            'partner_address': sd.partner_address,
          }
        elif sd.account_type == 'user' or sd.account_type == 'dame':
          lv = core_mo.LEVEL_RULE.objects.get(level=sd.user_level)
          level = {
            'level': sd.user_level,
            'text_color': lv.text_color,
            'background_color': lv.background_color,
            'name': lv.name,
          }
          sender = {
            'id': message.sender_id,
            'nickname': sd.first_name,
            'account_type': sd.account_type,
            'status': sd.status,
            'level': level,
          }

      # 쿠폰 정보
      if message.include_coupon:
        cu = coupon_mo.COUPON.objects.filter(code=message.include_coupon).first()
        cu_post = post_mo.POST.objects.filter(id=cu.post_id).first()
        post = {
          'id': cu.post_id,
          'title': cu_post.title,
        }
        coupon = {
          'code': cu.code,
          'name': cu.name,
          'post': post,
          'own_user_id': cu.own_user_id,
          'create_account_id': cu.create_account_id,
          'required_point': cu.required_point,
        }
      else:
        coupon = None

      search_messages.append({
        'id': message.id,
        'title': message.title,
        'sender': sender,
        'send_dt': message.send_dt,
        'read_dt': message.read_dt,
        'image': str(message.images).split(',')[0],
        'content': message.content,
        'include_coupon': coupon,
      })

    return render(request, 'supervisor/message.html', {
      **context,
      'search_messages': search_messages,
      'last_page': last_page,
      'status': status,
    })

  else:
    all_messages = message_mo.MESSAGE.objects.filter(sender_id='supervisor').order_by('-send_dt')
    status = {
      'outbox': {
        'count': all_messages.count(),
        'unread': all_messages.filter(read_dt=None).count(),
      }
    }

    # search
    sms = all_messages.filter(
      title__contains=search_message_title,
      sender_id='supervisor'
    )
    last_page = sms.count() // 20 + 1
    search_messages = []
    for message in sms[(page - 1) * 20:page * 20]:
      # 쪽지 수신자
      rc = get_user_model().objects.filter(username=message.receiver_id).first()
      if not rc:
        receiver = {
          'id': message.receiver_id,
          'nickname': '게스트',
          'account_type': 'guest',
          'status': 'active',
        }
      else:
        if rc.account_type == 'partner':
          receiver = {
            'id': message.receiver_id,
            'nickname': rc.first_name,
            'account_type': rc.account_type,
            'status': rc.status,
            'partner_categories': rc.partner_categories,
            'partner_address': rc.partner_address,
          }
        elif rc.account_type == 'user' or rc.account_type == 'dame':
          lv = core_mo.LEVEL_RULE.objects.get(level=rc.user_level)
          level = {
            'level': rc.user_level,
            'text_color': lv.text_color,
            'background_color': lv.background_color,
            'name': lv.name,
          }
          receiver = {
            'id': message.receiver_id,
            'nickname': rc.first_name,
            'account_type': rc.account_type,
            'status': rc.status,
            'level': level,
          }

      # 쿠폰 정보
      if message.include_coupon:
        cu = coupon_mo.COUPON.objects.filter(code=message.include_coupon).first()
        cu_post = post_mo.POST.objects.filter(id=cu.post_id).first()
        post = {
          'id': cu.post_id,
          'title': cu_post.title,
        }
        coupon = {
          'code': cu.code,
          'name': cu.name,
          'post': post,
          'own_user_id': cu.own_user_id,
          'create_account_id': cu.create_account_id,
          'required_point': cu.required_point,
        }
      else:
        coupon = None

      search_messages.append({
        'id': message.id,
        'title': message.title,
        'receiver': receiver,
        'send_dt': message.send_dt,
        'read_dt': message.read_dt,
        'image': str(message.images).split(',')[0],
        'content': message.content,
        'include_coupon': coupon,
      })

    return render(request, 'supervisor/message.html', {
      **context,
      'search_messages': search_messages,
      'last_page': last_page,
      'status': status,
    })

'''
def write_message(request):
  context = get_default_context(request)
  if context['account'] == None:
    return redirect('/')

  if request.method == 'POST':
    title = request.POST.get('title', '')
    receiver_id = request.POST.get('receiver_id', '')
    content = request.POST.get('content', '')
    message_mo.MESSAGE(
      title=title,
      sender_id='supervisor',
      receiver_id=receiver_id,
      content=content,
    ).save()
    return JsonResponse({'result': 'success'})
  return render(request, 'supervisor/write_message.html', context)

def read_message(request, message_id):
  context = get_default_context(request)
  if context['account'] == None:
    return redirect('/')

  message = message_mo.MESSAGE.objects.get(id=message_id)
  if message.receiver_id != 'supervisor':
    return redirect('/supervisor/message')
  if message.read_dt == '':
    message.read_dt = message.send_dt
    message.save()
  return render(request, 'supervisor/read_message.html', {
    **context,
    'message': {
      'id': message.id,
      'title': message.title,
      'sender': {
        'id': message.sender_id,
        'nickname': get_user_model().objects.get(username=message.sender_id).first_name,
      },
      'receiver': {
        'id': message.receiver_id,
        'nickname': get_user_model().objects.get(username=message.receiver_id).first_name,
      },
      'content': message.content,
      'send_dt': message.send_dt,
      'read_dt': message.read_dt,
    },
  })
'''

# 배너 관리 페이지
def banner(request):
  context = get_default_context(request)
  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if 'supervisor' not in context['account']['account_type']:
    return redirect('/?redirect=permission_denied')

  # 배너 생성 및 수정 요청 처리
  # 아이디가 있으면 수정, 없으면 생성
  if request.method == 'POST':
    id = request.POST.get('id')
    if id:
      banner = supervisor_mo.BANNER.objects.get(id=id)
      banner.location = request.POST.get('location', banner.location)
      banner.display_order = request.POST.get('display_order', banner.display_order)
      banner.image = request.POST.get('image', banner.image)
      banner.link = request.POST.get('link', banner.link)
      banner.save()
    else:
      supervisor_mo.BANNER(
        location = request.POST.get('location', ''),
        display_order = request.POST.get('display_order', ''),
        image = request.POST.get('image', ''),
        link = request.POST.get('link', ''),
      ).save()
    return JsonResponse({'result': 'success'})

  # 배너 삭제
  if request.method == 'DELETE':
    banner_id = request.GET.get('banner_id', '')
    supervisor_mo.BANNER.objects.get(id=banner_id).delete()
    return JsonResponse({'result': 'success'})

  # data
  banner_location = request.GET.get('tab', 'top')

  # search
  if banner_location == 'top':
    abs = supervisor_mo.BANNER.objects.filter(location='top').order_by('display_order')
  elif banner_location == 'side':
    abs = supervisor_mo.BANNER.objects.filter(location='side').order_by('display_order')
  all_banners = []
  for banner in abs:
    all_banners.append({
      'id': banner.id,
      'location': banner.location,
      'display_order': banner.display_order,
      'image': banner.image,
      'link': banner.link,
      'clicks': str(banner.clicks).split(','),
      'created_dt': banner.created_dt,
    })
  print(all_banners)
  return render(request, 'supervisor/banner.html', {
    **context,
    'banners': all_banners,
  })

# 레벨 관리 페이지
def level(request):
  context = get_default_context(request)
  if context['account'] == None:
    return redirect('/')

  # 레벨 생성 및 수정 요청 철;
  if request.method == 'POST':
    level = request.POST.get('level', '')
    text_color = request.POST.get('text_color', '')
    background_color = request.POST.get('background_color', '')
    name = request.POST.get('name', '')
    core_mo.LEVEL_RULE( # 그냥 덮어쓰기로 처리
      level=level,
      text_color=text_color,
      background_color=background_color,
      name=name,
    ).save()
    return JsonResponse({'result': 'success'})

  lvs = core_mo.LEVEL_RULE.objects.all().order_by('level')
  levels = []
  for level in lvs:
    levels.append({
      'level': level.level,
      'text_color': level.text_color,
      'background_color': level.background_color,
      'name': level.name,
    })


  return render(request, 'supervisor/level.html', {
    **context,
    'levels': levels,
  })

# 시스템 설정 페이지
def setting(request):
  context = get_default_context(request)
  if context == None:
    return redirect('/?redirect=permission_denied')
  if 'setting' not in context['account']['supervisor_permissions']:
    return redirect('/?redirect=permission_denied')

  # 설정 정보 변경 요청 처리
  if request.method == 'POST':
    id = request.POST.get('id', '')
    value = request.POST.get('value', '')
    core_mo.SERVER_SETTING( # 그냥 덮어쓰기로 처리
      id=id,
      value=value,
    ).save()
    return JsonResponse({'result': 'success'})

  all_settings = core_mo.SERVER_SETTING.objects.all()
  return render(request, 'supervisor/setting.html', {
    **context,
    'settings': [{
      'id': setting.id,
      'value': setting.value,
    } for setting in all_settings],
  })
