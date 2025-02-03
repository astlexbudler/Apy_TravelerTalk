import datetime
import math
import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, get_user_model
from django.db.models import Q

from app_core import models
from app_core import daos

# 관리자 메인 페이지
def index(request):
  contexts = daos.get_default_contexts(request)

  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없음 메세지 표시
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=permission_denied')
  if 'supervisor' not in contexts['account']['groups']:
    return redirect('/?redirect_message=permission_denied')
  return render(request, 'supervisor/index.html', contexts)

# 계정 관리 페이지
# 계정별 마지막 로그인 시간 및 회원가입일, 관리자 노트 등 포함
# 관리자 생성 및 사용자 정보 수정 기능 포함(삭제도 사용자 정보 수정으로 가능)
def account(request):
  contexts = daos.get_default_contexts(request)
  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=permission_denied')
  if 'supervisor' not in contexts['account']['groups'] and 'subsupervisor' not in contexts['account']['groups']:
    return redirect('/?redirect_message=permission_denied')

  # 관리자 신규 생성 처리
  # method='POST', action='create_supervisor'일 경우, 관리자 계정 생성 요청으로 처리
  '''
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
  '''

  # data
  tab = request.GET.get('tab', 'user') # user, dame, partner, supervisor
  page = int(request.GET.get('page', '1'))
  search_account_id = request.GET.get('accountId', '')
  search_account_nickname = request.GET.get('accountNickname', '')
  search_account_status = request.GET.get('accountStatus', '')

  # 계정 타입별로 계정 통계 가져오기
  # 관리자 계정 탭은 별도의 통계 없음.
  # 파트너는 각 카테고리면 파트너 계정 통계 제공
  # 사용자는 사용자 및 여성 회원의 계정 통계 제공
  all_accounts = get_user_model().objects.all().order_by('-date_joined')
  if tab == 'supervisor': # 관리자 검색 탭일 경우, 별도의 사용자 통계 기능 없음.
    status = {}
  elif tab == 'user': # 사용자 검색 탭일 경우, 사용자 및 여성회원 정보 제공
    dame_accounts = all_accounts.exclude(
      groups__name__in=['partner', 'supervisor', 'subsupervisor']
    ).filter(
      Q(groups__name='dame') | Q(status='pending_dame')
    )
    user_accounts = all_accounts.exclude(
      groups__name__in=['partner', 'supervisor', 'subsupervisor', 'dame']
    ).filter(
      groups__name='user'
    )
    status = {
      'user': {
        'active': user_accounts.filter(status='active').count(),
        'pending': 0,
        'deleted': user_accounts.filter(status='deleted').count(),
        'blocked': user_accounts.filter(status='blocked').count(),
        'banned': user_accounts.filter(status='banned').count(),
      },
      'dame': {
        'active': dame_accounts.filter(status='active').count(),
        'pending': dame_accounts.filter(status='pending_dame').count(),
        'deleted': dame_accounts.filter(status='deleted').count(),
        'blocked': dame_accounts.filter(status='blocked').count(),
        'banned': dame_accounts.filter(status='banned').count(),
      }
    }
  elif tab == 'partner': # 파트너 검색 탭일 경우, 파트너 정보 제공
    partner_accounts = all_accounts.filter(
      Q(groups__name='partner') | Q(status='pending_partner')
    )
    status = {
      'partner': {
        'active': partner_accounts.filter(status='active').count(),
        'pending': partner_accounts.filter(status='pending_partner').count(),
        'deleted': partner_accounts.filter(status='deleted').count(),
        'blocked': partner_accounts.filter(status='blocked').count(),
        'banned': partner_accounts.filter(status='banned').count(),
      }
    }
  # 사용자 검색
  if tab == 'user': # 사용자 탭일 경우, user와 dame을 같이 검색
    sats = all_accounts.exclude(
      groups__name__in=['partner', 'supervisor', 'subsupervisor']
    ).select_related('level').filter(
      Q(username__contains=search_account_id) | Q(first_name__contains=search_account_nickname) | Q(status__contains=search_account_status)
    )
  elif tab == 'supervisor': # 관리자 탭일 경우, 관리자만 검색
    sats = all_accounts.filter(
      Q(groups__name='supervisor') | Q(groups__name='subsupervisor'),
      Q(username__contains=search_account_id) | Q(first_name__contains=search_account_nickname) | Q(status__contains=search_account_status)
    )
  elif tab == 'partner': # 파트너 탭일 경우, 파트너만 검색
    sats = all_accounts.filter(
      Q(groups__name='partner') | Q(status__contains='pending_partner'),
      Q(username__contains=search_account_id) | Q(first_name__contains=search_account_nickname) | Q(status__contains=search_account_status)
    )

  last_page = sats.count() // 20 + 1 # 20개씩 표시
  search_accounts = []
  for account in sats[(page - 1) * 20:page * 20]:

    # 계정 정보
    search_accounts.append({
      'id': account.username,
      'nickname': account.first_name,
      'partner_name': account.last_name,
      'email': account.email,
      'groups': [group.name for group in account.groups.all()],
      'date_joined': account.date_joined,
      'last_login': account.last_login,
      'status': account.status,
      'note': account.note,
      'coupon_point': account.coupon_point,
      'level_point': account.level_point,
      'tel': account.tel,
      'subsupervisor_permissions': account.subsupervisor_permissions,
      'level': {
        'level': account.level.level,
        'image': account.level.image,
        'text': account.level.text,
        'text_color': account.level.text_color,
        'background_color': account.level.background_color,
        'required_point': account.level.required_point,
      } if account.level else None,
    })

  return render(request, 'supervisor/account.html', {
    **contexts,
    'accounts': search_accounts, # 검색된 계정 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
    'status': status, # 사용자 종류(탭) 별 통계 데이터(관리자는 없음)
  })

# 게시글 관리 페이지
def post(request):
  contexts = daos.get_default_contexts(request)

  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=permission_denied')
  if 'supervisor' not in contexts['account']['groups'] and 'subsupervisor' not in contexts['account']['groups']:
    return redirect('/?redirect_message=permission_denied')

  # post_id 게시글 강제 삭제
  '''
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
  '''

  # data
  page = int(request.GET.get('page', '1'))
  search_post_title = request.GET.get('post_title', '')
  search_board_id = request.GET.get('board_id', '')

  # status
  # 각 게시판 별 게시글 수와 댓글 수, 조회수, 좋아요 수 통계 제공
  all_post = models.POST.objects.prefetch_related('boards').select_related('author', 'place_info', 'review_post').prefetch_related('place_info__categories').all()
  boards = models.BOARD.objects.all().order_by('display_weight')
  board_dict = {
    board.name: {
      'id': board.id,
      'name': board.name,
      'board_type': board.board_type,
      'total_views': int(math.fsum([post.view_count for post in models.POST.objects.filter(Q(boards__id__in=str(board.id)))])),
      'total_posts': models.POST.objects.filter(Q(boards__id__in=str(board.id))).count(),
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
          'total_views': int(math.fsum([post.view_count for post in models.POST.objects.filter(Q(boards__id__in=str(board.id)))])),
          'total_posts': models.POST.objects.filter(Q(boards__id__in=str(board.id))).count(),
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
                'total_views': int(math.fsum([post.view_count for post in models.POST.objects.filter(Q(boards__id__in=str(board.id)))])),
                'total_posts': models.POST.objects.filter(Q(boards__id__in=str(board.id))).count(),
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
                    'total_views': int(math.fsum([post.view_count for post in models.POST.objects.filter(Q(boards__id__in=str(board.id)))])),
                    'total_posts': models.POST.objects.filter(Q(boards__id__in=str(board.id))).count(),
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
    Q(title__contains=search_post_title),
    Q(boards__id__contains=search_board_id),
  )
  last_page = sps.count() // 20 + 1 # 20개씩 표시
  search_posts = []
  for post in sps[(page - 1) * 20:page * 20]:

    search_posts.append({
      'id': post.id,
      'title': post.title,
      'image_paths': post.image_paths, # 여행지 또는 리뷰, 이벤트 게시글의 대표 이미지 경로
      'view_count': post.view_count,
      'like_count': post.like_count,
      'created_at': post.created_at,
      'author': {
        'nickname': post.author.first_name, # 작성자 닉네임
        'partner_name': post.author.last_name, # 작성자 파트너 이름
      },
      'place_info': { # 여행지 게시글인 경우, 여행지 정보
        'categories': [c.name for c in post.place_info.categories.all()],
        'address': post.place_info.address,
        'location_info': post.place_info.location_info,
        'open_info': post.place_info.open_info,
        'status': post.place_info.status,
      } if post.place_info else None,
      'review_post': { # 리뷰 게시글인 경우, 리뷰 대상 게시글 정보
        'id': post.review_post.id,
        'title': post.review_post.title,
      } if post.review_post else None,
    })

  return render(request, 'supervisor/post.html', {
    **contexts,
    'posts': search_posts, # 검색된 게시글 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
    'status': boards, # 게시판 별 통계 데이터. 게시판 별로 게시글 수, 댓글 수, 조회수, 좋아요 수 제공
  })

'''
# 광고 게시글 관리 페이지
def ad_post(request):
  context = get_default_context(request)
  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if 'supervisor' not in context['account']['account_type']:
    return redirect('/?redirect_message=permission_denied')

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
'''

# 쿠폰 관리 페이지
# 별도의 쿠폰 수정 삭제 기능은 없음
def coupon(request):
  contexts = daos.get_default_contexts(request)

  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=permission_denied')
  if 'supervisor' not in contexts['account']['groups'] and 'subsupervisor' not in contexts['account']['groups']:
    return redirect('/?redirect_message=permission_denied')

  # data
  tab_type = request.GET.get('tab', 'coupon') # coupon, history
  page = int(request.GET.get('page', '1'))
  search_coupon_code = request.GET.get('coupon_code', '')
  search_coupon_name = request.GET.get('coupon_name', '')

  # status
  if tab_type == 'coupon':
    cs = models.COUPON.objects.select_related('post', 'create_account').prefetch_related('own_accounts').exclude(
      Q(status='deleted') | Q(status='used') | Q(status='expired')
    ).filter(
      code__contains=search_coupon_code,
      name__contains=search_coupon_name,
    ).order_by('-created_at')
  elif tab_type == 'history':
    cs = models.COUPON.objects.select_related('post', 'create_account').prefetch_related('own_accounts').exclude(
      Q(status='normal')
    ).filter(
      code__contains=search_coupon_code,
      name__contains=search_coupon_name,
    ).order_by('-created_at')
  last_page = cs.count() // 20 + 1 # 20개씩 표시
  coupons = []
  for coupon in cs[(page - 1) * 20:page * 20]:
    coupons.append({
      'code': coupon.code,
      'name': coupon.name,
      'image': coupon.image,
      'content': coupon.content,
      'required_point': coupon.required_point,
      'expire_at': coupon.expire_at,
      'status': coupon.status,
      'post': {
        'id': coupon.post.id,
        'title': coupon.post.title,
      },
      'create_account': {
        'partner_name': coupon.create_account.last_name,
      },
    })

  return render(request, 'supervisor/coupon.html', {
    **contexts,
    'coupons': coupons, # 검색된 쿠폰 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
  })


# 쪽지 관리 페이지
def message(request):
  contexts = daos.get_default_contexts(request)

  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=permission_denied')
  if 'supervisor' not in contexts['account']['groups'] and 'subsupervisor' not in contexts['account']['groups']:
    return redirect('/?redirect_message=permission_denied')

  # data
  tab = request.GET.get('tab', 'inbox') # inbox, outbox
  page = int(request.GET.get('page', '1'))
  search_message_title = request.GET.get('message_title', '')
  search_message_receiver = request.GET.get('message_receiver', '')

  # 받은 쪽지함
  if tab == 'inbox':
    msgs = models.MESSAGE.objects.select_related('include_coupon').filter(
      to_account='supervisor',
      title__contains=search_message_title,
      sender_account__contains=search_message_receiver,
    )
    last_page = len(msgs) // 20 + 1
    messages = [{
      'id': m.id,
      'title': m.title,
      'content': m.content,
      'is_read': m.is_read,
      'created_at': m.created_at,
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
          'image': sd.level.image,
          'text': sd.level.text,
          'text_color': sd.level.text_color,
          'background_color': sd.level.background_color,
        } if sd.level else None,
        'groups': [g.name for g in sd.groups.all()],
      } if (sd := get_user_model().objects.prefetch_related('groups').select_related('level').get(username=m.sender_account)) else {'id': m.sender_account},
    } for m in msgs[(page - 1) * 20:page * 20]]

    return render(request, 'supervisor/message.html', {
      **contexts,
      'messages': messages,
      'last_page': last_page,
    })

  elif tab == 'outbox':
    msgs = models.MESSAGE.objects.select_related('include_coupon').filter(
      sender_account='supervisor',
      title__contains=search_message_title,
      to_account__contains=search_message_receiver,
    )
    last_page = len(msgs) // 20 + 1
    messages = [{
      'id': m.id,
      'title': m.title,
      'content': m.content,
      'is_read': m.is_read,
      'created_at': m.created_at,
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
          'image': rc.level.image,
          'text': rc.level.text,
          'text_color': rc.level.text_color,
          'background_color': rc.level.background_color,
        } if rc.level else None,
        'groups': [g.name for g in rc.groups.all()],
      } if (rc := get_user_model().objects.prefetch_related('groups').select_related('level').get(username=m.to_account)) else {'id': m.to_account},
    } for m in msgs[(page - 1) * 20:page * 20]]

    return render(request, 'supervisor/message.html', {
      **contexts,
      'messages': messages,
      'last_page': last_page,
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
  contexts = daos.get_default_contexts(request)

  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=permission_denied')
  if 'supervisor' not in contexts['account']['groups'] and 'subsupervisor' not in contexts['account']['groups']:
    return redirect('/?redirect_message=permission_denied')

  # 배너 생성 및 수정 요청 처리
  # 아이디가 있으면 수정, 없으면 생성
  '''
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
  '''

  # search
  banners = {
    'top': [], # 상단 배너
    'side': [], # 사이드 및 하단 배너
  }
  for b in models.BANNER.objects.all().order_by('display_weight'):
    banners['top'].append({
      'id': b.id,
      'location': b.location,
      'image': b.image,
      'link': b.link,
      'display_weight': b.display_weight,
    })

  return render(request, 'supervisor/banner.html', {
    **contexts,
    'banners': banners,
  })

# 레벨 관리 페이지
def level(request):
  contexts = daos.get_default_contexts(request)

  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=permission_denied')
  if 'supervisor' not in contexts['account']['groups'] and 'subsupervisor' not in contexts['account']['groups']:
    return redirect('/?redirect_message=permission_denied')

  '''
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
  '''

  lvs = models.LEVEL_RULE.objects.all().order_by('level')
  levels = [{
    'level': lv.level,
    'image': lv.image,
    'text': lv.text,
    'text_color': lv.text_color,
    'background_color': lv.background_color,
    'required_point': lv.required_point,
  } for lv in lvs]

  return render(request, 'supervisor/level.html', {
    **contexts,
    'levels': levels,
  })

# 시스템 설정 페이지
def setting(request):
  contexts = daos.get_default_contexts(request)

  # 관리자 여부 확인, 관리자가 아닌 경우, 리다이렉트 후 권한 없은 메세지 표시
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=permission_denied')
  if 'supervisor' not in contexts['account']['groups'] and 'subsupervisor' not in contexts['account']['groups']:
    return redirect('/?redirect_message=permission_denied')

  '''
  # 설정 정보 변경 요청 처리
  if request.method == 'POST':
    id = request.POST.get('id', '')
    value = request.POST.get('value', '')
    core_mo.SERVER_SETTING( # 그냥 덮어쓰기로 처리
      id=id,
      value=value,
    ).save()
    return JsonResponse({'result': 'success'})
  '''

  sts = models.SERVER_SETTING.objects.all()
  settings = [{
    'name': st.name,
    'value': st.value,
  } for st in sts]

  return render(request, 'supervisor/setting.html', {
    **contexts,
    'settings': settings,
  })