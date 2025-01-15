from datetime import datetime
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

from app_core import daos as core_do
from app_user import daos as user_do
from app_message import daos as message_do
from app_post import daos as post_do

# 기본 컨텍스트
# server, account
def get_default_context(request):

  # 사용자 프로필 정보 가져오기
  # 로그인하지 않은 사용자는 guest로 처리
  account = user_do.get_user_profile(request)

  # 서버 설정 가져오기
  server = core_do.get_server_settings()

  # 광고 게시글 가져오기
  # 모든 파트너 계정은 최대 1개의 광고 게시글을 가질 수 있음.
  tp = post_mo.POST.objects.exclude(
    ad_id='', # 광고 게시글은 반드시 광고 ID가 있음
  ).filter(
    author_id=account['id'], # 파트너 계정 ID
  ).first() # 광고 게시글은 최대 1개만 존재함
  travel_post = None
  if tp: # 광고 게시글이 있는 경우
    # 게시판은 tree형태로 구성되어 있음
    boards = []
    bos = str(tp.board_id).split(',')
    for bo in bos:
      if bo != '':
        board = post_mo.BOARD.objects.get(id=bo)
        boards.append({
          'id': board.id,
          'name': board.name,
        })
    travel_post = {
      'id': tp.id,
      'boards': boards, # 여행 > 국내 > 서울 > 강남 이런 식으로 표시됨
      'title': tp.title,
      'images': str(tp.images).split(','), # 이미지
      'content': tp.content,
      'created_dt': tp.created_dt,
      'view_count': len(str(tp.views).split(',')) - 1, # 조회수
      'bookmark_count': len(str(tp.bookmarks).split(',')) - 1, # 북마크 수(좋아요 수)
      'comment_count': post_mo.COMMENT.objects.filter(post_id=tp.id).count(), # 댓글 수
      'created_dt': tp.created_dt,
      'author': { # 작성자 정보(파트너 본인)
        'id': tp.author_id,
        'nickname': account['nickname'],
        'partner_address': account['partner_address'],
        'partner_categories': account['partner_categories'],
      }
    }

  return {
    'server': server,
    'account': account,
    'travel_post': travel_post,
  }

# 파트너 관리자 메인 페이지
def index(request):
  context = get_default_context(request)
  # 파트너 계정이 아닌 경우, 홈으로 이동
  if context['account']['account_type'] != 'partner':
    return redirect('/?redirect=partner_status_error')

  return render(request, 'partner/index.html', {
    **context,
    'profile': context['account'],
  })

# 새 광고 게시글 작성 페이지
def write_post(request):
  context = get_default_context(request)
  # 파트너 계정이 아닌 경우, 홈으로 이동
  if context['account']['account_type'] != 'partner':
    return redirect('/?redirect=partner_status_error')

  # 광고 게시글이 이미 있는 경우, 광고 게시글 수정 페이지로 이동
  if context['travel_post']:
    return redirect('/partner/rewrite_post')

  # 광고 게시글 작성
  if request.method == 'POST':
    title = request.POST.get('title', '')
    content = request.POST.get('content', '')
    images = request.POST.get('images', '')
    board_id = request.POST.get('board_ids', '') # 게시판 ID(여러 개일 수 있음)

    # 새 광고 정책 생성
    ad = post_mo.AD(
      status='expired',
      weight=0,
      note='',
      post_id='',
    )
    ad.save()

    # 광고 게시글 생성
    post = post_mo.POST(
      board_id=board_id,
      ad_id=ad.id,
      author_id=request.user.username,
      title=title,
      content=content,
      images=images,
    )
    post.save()

    ad.post_id = post.id
    ad.save()

    # 사용자 활동 기록
    act = user_mo.ACTIVITY(
      user_id=request.user.username,
      location='/post/travel_view?post=' + str(post.id),
      message='[파트너] 광고 게시글 작성. (' + title + ')',
      point_change=0,
    )
    act.save()

    return JsonResponse({
      'result': 'success',
      'post_id': post.id,
    })

  # 게시판 정보
  boards = post_do.get_boards()

  return render(request, 'partner/write_post.html', {
    **context,
    'boards': boards,
  })

# 광고 게시글 수정 페이지
def rewrite_post(request):
  context = get_default_context(request)
  if context['account']['account_type'] != 'partner':
    return redirect('/?redirect=partner_status_error')

  # 광고 게시글이 없으면, 광고 게시글 작성 페이지로 이동
  if not context['travel_post']:
    return redirect('/partner/write_post?redirect=need_travel_post')

  # 광고 게시글 수정
  # title, content, images, board_id 수정 가능
  if request.method == 'POST':
    tp = post_mo.POST.objects.get(id=context['travel_post']['id'])
    title = request.POST.get('title', tp.title)
    content = request.POST.get('content', tp.content)
    images = request.POST.get('images', tp.images)
    board_id = request.POST.get('board_ids', tp.board_id)
    tp.title = title
    tp.content = content
    tp.images = images
    tp.board_id = board_id
    tp.save()

    # 사용자 활동 기록
    act = user_mo.ACTIVITY(
      user_id=request.user.username,
      location='/post/travel_view?post=' + str(tp.id),
      message='[파트너] 광고 게시글 수정. (' + title + ')',
      point_change=0,
    )
    act.save()

  # 광고 게시글 삭제 요청
  if request.method == 'DELETE':
    tp = post_mo.POST.objects.get(id=context['travel_post']['id'])

    # 광고 정책 삭제
    ad = post_mo.AD.objects.get(id=tp.ad_id)
    ad.delete()

    # 사용자 활동 기록 작성
    act = user_mo.ACTIVITY(
      user_id=request.user.username,
      location='',
      message='[파트너] 여행지 게시글 삭제. (' + tp.title + ')',
      point_change=0,
    )
    act.save()

    # 광고 게시글 삭제
    tp.delete()

    return JsonResponse({
      'result': 'success',
    })

  # 게시판 정보
  boards = post_do.get_boards()

  return render(request, 'partner/rewrite_post.html', {
    **context,
    'boards': boards,
  })

# 쿠폰 관리 페이지
def coupon(request):
  context = get_default_context(request)
  if context['account']['account_type'] != 'partner':
    return redirect('/?redirect=partner_status_error')

  # 여행 게시글
  tp = post_mo.POST.objects.exclude(
    ad_id='', # 광고 게시글은 반드시 광고 ID가 있음
  ).filter(
    author_id=context['account']['id'], # 파트너 계정 ID
  ).first() # 광고 게시글은 1개만 존재함
  travel_post = None
  if tp:
    travel_post = {
      'id': tp.id,
      'title': tp.title,
    }
  else: # 광고 게시글이 없는 경우, 광고 게시글 작성 페이지로 이동
    return redirect('/partner/write_post?redirect=need_travel_post')

  # 새 쿠폰 생성
  if request.method == 'POST':
    code = request.POST.get('code', '') # 쿠폰 코드
    name = request.POST.get('name', '') # 쿠폰 이름
    description = request.POST.get('description', '') # 쿠폰 설명
    images = request.POST.get('image', '') # 쿠폰 이미지(이미지는 1개만 등록 가능)
    # 필요 포인트는 나중에 사용자가 쿠폰을 사용할 때, 포인트가 부족하면 사용할 수 없도록 함.
    required_point = request.POST.get('require_point', '') # 필요 포인트

    # 쿠폰 코드 생성
    coupon = coupon_mo.COUPON(
      code=code,
      create_account_id=request.user.username, # 파트너 본인 ID
      own_user_id=request.user.username, # 쿠폰 소유자 ID(파트너 본인)
      name=name,
      description=description,
      images=images,
      post_id=travel_post['id'], # 쿠폰과 연결된 게시글 ID(광고 게시글 ID)
      required_point=required_point,
    )
    coupon.save()

    # 사용자 활동 기록
    act = user_mo.ACTIVITY(
      user_id=request.user.username,
      location='/partner/coupon',
      message='[파트너] 새 쿠폰 생성. (' + name + ')',
      point_change=0,
    )
    act.save()

    return JsonResponse({
      'result': 'success',
      'coupon_id': coupon.id,
    })

  # 쿠폰 정보 수정. code를 제외한 나머지 정보 수정 가능. 또는 쿠폰 사용 처리
  if request.method == 'PATCH':
    coupon_id = request.GET.get('coupon_id', '')

    # 쿠폰 사용자 정보가 있는 경우, 쿠폰 사용 처리
    status = request.GET.get('status', '') # used, expired, deleted
    if status:
      coupon = coupon_mo.COUPON.objects.filter(id=coupon_id).first()
      coupon_use_user = get_user_model().objects.filter(username=coupon.own_user_id).first()
      note = request.GET.get('note', '')

      # 쿠폰 포인트 차감
      if status == 'used':
        coupon_use_user.user_usable_point -= coupon.required_point
        if coupon_use_user.user_usable_point < 0: # 포인트 부족 시 쿠폰 사용 불가
          return JsonResponse({'result': 'not_enough_point'})
        coupon_use_user.save()

      # 쿠폰 사용 기록 생성
      coupon_history = coupon_mo.COUPON_HISTORY(
        code=coupon.code,
        create_account_id=coupon.create_account_id,
        used_user_id=coupon.own_user_id,
        name=coupon.name,
        description=coupon.description,
        images=coupon.images,
        post_id=coupon.post_id,
        required_point=coupon.required_point,
        status=status,
        note=note,
      )
      coupon_history.save()

      # 쿠폰 삭제
      coupon.delete()

      # 사용자 활동 기록
      act = user_mo.ACTIVITY(
        user_id=request.user.username,
        location='/partner/coupon',
        message='[파트너] 쿠폰 사용 처리. (' + coupon.name + ')',
        point_change=0,
      )
      act.save()

      return JsonResponse({
        'result': 'success',
        'coupon_history_id': coupon_history.id,
      })

    # 쿠폰 정보 수정
    coupon = coupon_mo.COUPON.objects.filter(id=coupon_id).first()
    if not coupon:
      return JsonResponse({'result': 'coupon_not_found'})
    name = request.GET.get('name', coupon.name)
    description = request.GET.get('description', coupon.description)
    images = request.GET.get('image', coupon.images)
    required_point = request.GET.get('require_point', coupon.required_point)
    coupon.name = name
    coupon.description = description
    coupon.images = images
    coupon.required_point = required_point
    coupon.save()

    # 사용자 활동 기록
    act = user_mo.ACTIVITY(
      user_id=request.user.username,
      location='/partner/coupon',
      message='[파트너] 쿠폰 정보 수정. (' + name + ')',
      point_change=0,
    )
    act.save()

    return JsonResponse({
      'result': 'success',
      'coupon_id': coupon.id,
    })

  # 쿠폰 삭제(삭제된 쿠폰은 쿠폰 히스토리로 이동됨.)
  if request.method == 'DELETE':
    coupon_id = request.GET.get('coupon_id', '')
    status = request.GET.get('status', 'deleted') # 쿠폰 상태 지정(used, expired, deleted)
    note = request.GET.get('note', '')
    print(coupon_id, status, note)

    # 쿠폰 확인
    coupon = coupon_mo.COUPON.objects.filter(id=coupon_id).first()
    if not coupon:
      return JsonResponse({'result': 'coupon_not_found'})

    # 쿠폰 히스토리 생성
    coupon_history = coupon_mo.COUPON_HISTORY(
      code=coupon.code,
      create_account_id=coupon.create_account_id,
      used_user_id=coupon.own_user_id,
      name=coupon.name,
      description=coupon.description,
      images=coupon.images,
      post_id=coupon.post_id,
      required_point=coupon.required_point,
      status=status,
      note=note,
      created_dt=coupon.created_dt,
    )
    coupon_history.save()

    # 쿠폰 삭제
    coupon.delete()

    # 사용자 활동 기록
    act = user_mo.ACTIVITY(
      user_id=request.user.username,
      location='/partner/coupon',
      message='[파트너] 쿠폰 삭제. (' + coupon.name + ')',
      point_change=0,
    )
    act.save()

    return JsonResponse({
      'result': 'success',
      'coupon_history_id': coupon_history.id,
    })

  # data
  page = int(request.GET.get('page', 1))
  tab = request.GET.get('tab', 'coupon') # coupon, history
  search_coupon_code = request.GET.get('search_coupon_code', '')
  search_coupon_name = request.GET.get('search_coupon_name', '')

  # search
  if tab == 'coupon': # 쿠폰 목록 탭

    # 쿠폰 목록 가져오기
    cps = coupon_mo.COUPON.objects.filter(
      create_account_id = request.user.username,
      code__contains = search_coupon_code,
      name__contains = search_coupon_name,
    ).order_by('-created_dt')
    coupons = []
    last_page = len(cps) // 30 + 1 # 한 페이지당 30개씩 표시
    for cp in cps[(page - 1) * 30:page * 30]:

      # 쿠폰 소유자 정보
      if cp.own_user_id != request.user.username:
        ou = get_user_model().objects.filter(username=cp.own_user_id).first()
        own_user = {
          'id': ou.username,
          'nickname': ou.first_name,
        }
      else:
        own_user = {
          'id': request.user.username,
          'nickname': request.user.first_name,
        }

      coupons.append({
        'id': cp.id,
        'code': cp.code,
        'name': cp.name,
        'description': cp.description,
        'images': str(cp.images).split(','),
        'post_id': cp.post_id,
        'created_dt': cp.created_dt,
        'required_point': cp.required_point,
        'own_user': own_user,
        'post': travel_post,
      })
    return render(request, 'partner/coupon.html', {
      **context,
      'last_page': last_page,
      'coupons': coupons,
    })

  elif tab == 'history': # 쿠폰 사용 내역 탭
    hs = coupon_mo.COUPON_HISTORY.objects.filter(
      create_account_id = request.user.username,
      code__contains = search_coupon_code,
      name__contains = search_coupon_name,
    ).order_by('-created_dt')
    histories = []
    last_page = len(hs) // 30 + 1 # 한 페이지당 30개씩 표시
    for h in hs[(page - 1) * 30:page * 30]:

      # 쿠폰 사용자 정보
      if h.used_user_id != request.user.username:
        uu = get_user_model().objects.filter(username=h.used_user_id).first()
        used_user = {
          'id': uu.username,
          'nickname': uu.first_name,
        }
      else:
        used_user = {
          'id': request.user.username,
          'nickname': request.user.first_name,
        }

      histories.append({
        'id': h.id,
        'code': h.code,
        'name': h.name,
        'description': h.description,
        'images': str(h.images).split(','),
        'post_id': h.post_id,
        'created_dt': h.created_dt,
        'used_dt': h.used_dt,
        'required_point': h.required_point,
        'status': h.status,
        'note': h.note,
        'used_user': used_user,
        'post': travel_post,
      })

    return render(request, 'partner/coupon.html', {
      **context,
      'last_page': last_page,
      'histories': histories,
    })