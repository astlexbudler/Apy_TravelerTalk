from datetime import datetime
import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout
from django.db.models import Q
from django.conf import settings

from app_core import models
from app_core import daos

# 파트너 관리자 메인 페이지
def index(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기

  if contexts['account']['account_type'] != 'partner': # 파트너 계정이 아닌 경우
    return redirect(settings.MAIN_URL + '/?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 사용자 프로필 정보
  profile = daos.get_user_profile_by_id(contexts['account']['id'])

  # 파트너 계정이 소유한 여행지 게시글
  p = models.POST.objects.filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).first()
  if not p: # 여행지 게시글이 없는 경우, 광고 게시글 작성 페이지로 이동
    return redirect('write_post?redirect_message=need_travel_post')
  post = daos.get_post_info(p.id)

  return render(request, 'partner/index.html', {
    **contexts,
    'profile': profile, # 사용자 프로필 정보
    'post': post, # 여행지 게시글 정보
  })

# 새 광고 게시글 작성 페이지*사용하지 않음
def write_post(request):
  return redirect('/rewrite_post') # 임시로 광고 게시글 수정 페이지로 이동

  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기

  if contexts['account']['account_type'] != 'partner': # 파트너 계정이 아닌 경우
    return redirect('/?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 광고 게시글이 이미 있는 경우, 광고 게시글 수정 페이지로 이동
  p = models.POST.objects.filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).first()
  if p: # 여행지 게시글이 있는 경우
    return redirect('/rewrite_post?redirect_message=travel_post_exist')

  # 광고 게시글 작성
  '''
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
    act = models.ACTIVITY(
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
  '''

  # 게시판 정보
  boards = daos.get_board_tree()

  # 카테고리 정보
  categories = daos.get_category_tree()

  return render(request, 'partner/write_post.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'categories': categories, # 카테고리 정보
  })

# 광고 게시글 수정 페이지
def rewrite_post(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기

  if contexts['account']['account_type'] != 'partner': # 파트너 계정이 아닌 경우
    return redirect(settings.MAIN_URL + '/?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 광고 게시글 정보
  p = models.POST.objects.filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).first()
  if not p: # 여행지 게시글이 없는 경우, 광고 게시글 작성 페이지로 이동
    return redirect('/?redirect_message=travel_post_not_exist') # 홈으로 리다이렉트
  post = daos.get_post_info(p.id)

  # 광고 게시글 작성지 확인
  if contexts['account']['id'] != post['author']['id']:  # 광고 게시글 작성자가 아닌 경우
    return redirect('/?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 광고 게시글 수정
  if request.method == 'POST':
    po = models.POST.objects.select_related('place_info').get(id=post['id'])

    title = request.POST.get('title', po.title)
    content = request.POST.get('content', po.content)
    board_ids = str(request.POST.get('board_ids')).split(',') # 게시판 ID(여러 개일 수 있음)
    service_ids = str(request.POST.get('service_ids')).split(',') # 서비스 ID(여러 개일 수 있음)
    location_info = request.POST.get('location_info', po.place_info.location_info)
    open_info = request.POST.get('open_info', po.place_info.open_info)
    address = request.POST.get('address', po.place_info.address)
    place_status = request.POST.get('place_status')
    image = request.FILES.get('image', post['image'])

    # 만약 기존 광고 상태가 'ad'인 경우, 광고 상태 유지
    if po.place_info.status == 'ad':
      place_status = 'ad'

    # 이미지가 없는 경우, 기존 이미지 유지
    if image:
      po.image = image

    # 광고 게시글 수정
    po.title = title
    po.content = content
    po.save()
    po.place_info.location_info = location_info
    po.place_info.open_info = open_info
    po.place_info.address = address
    po.place_info.status = place_status
    po.place_info.save()

    # 게시판 정보 수정
    if board_ids != ['']:
      po.board.clear()
      for board_id in board_ids:
        board = models.BOARD.objects.get(id=board_id)
        po.board.add(board)

    # 서비스 정보 수정
    if service_ids != ['']:
      po.place_info.categories.clear()
      for service_id in service_ids:
        service = models.CATEGORY.objects.get(id=service_id)
        po.place_info.categories.add(service)
    po.save()
    po.place_info.save()

    # 사용자 활동 기록
    models.ACTIVITY.objects.create(
      account=request.user,
      message='[파트너] 여행지 게시글을 수정했습니다. (' + title + ')',
    )

    return JsonResponse({
      'result': 'success',
      'post_id': po.id,
    })

  # 게시판 정보
  boards = daos.get_travel_board_tree()

  # 카테고리 정보
  categories = daos.get_category_tree()

  return render(request, 'partner/rewrite_post.html', {
    **contexts,
    'post': post, # 여행지 게시글 정보
    'boards': boards, # 게시판 정보
    'categories': categories, # 카테고리 정보
  })

# 쿠폰 관리 페이지
def coupon(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  account_type = 'guest' # 기본값은 guest
  if request.user.is_authenticated:
    account_type = 'user'
    if 'dame' in contexts['account']['groups']:
      account_type = 'dame'
    elif 'partner' in contexts['account']['groups']:
      account_type = 'partner'
    elif 'subsupervisor' in contexts['account']['groups']:
      account_type = 'subsupervisor'
    elif 'supervisor' in contexts['account']['groups']:
      account_type = 'supervisor'
  contexts['account']['account_type'] = account_type
  if not request.user.is_authenticated: # 로그인 되지 않은 경우
    return redirect(settings.MAIN_URL + '/?redirect_message=need_login') # 로그인 필요 메세지 표시
  if account_type != 'partner': # 파트너 계정이 아닌 경우
    return redirect(settings.MAIN_URL + '/?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 여행지 게시글
  p = models.POST.objects.filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).first()
  if not p: # 여행지 게시글이 없는 경우, 광고 게시글 작성 페이지로 이동
    return redirect('/?redirect_message=travel_post_not_exist') # 홈으로 리다이렉트
  post = daos.get_post_info(p.id)

  # 데이터 가져오기
  tab = request.GET.get('tab', 'coupon') # coupopn, history
  page = int(request.GET.get('page', 1))
  search_coupon_code = request.GET.get('code', '') # 쿠폰 이름 검색
  search_coupon_name = request.GET.get('name', '') # 쿠폰 소유자 검색

  # 쿠폰 목록 가져오기
  if tab == 'coupon': # 쿠폰 목록
    cps = models.COUPON.objects.select_related('post').prefetch_related('own_accounts').filter(
      create_account=request.user,
      name__contains=search_coupon_name,
      code__contains=search_coupon_code,
      status='active',
    ).order_by('-expire_at')
  elif tab == 'history': # 쿠폰 사용 내역
    cps = models.COUPON.objects.select_related('post').prefetch_related('own_accounts').exclude(
      status='active',
    ).filter(
      create_account=request.user,
      name__contains=search_coupon_name,
      code__contains=search_coupon_code,
    ).order_by('-expire_at')
  coupons = []
  last_page = len(cps) // 30 + 1 # 한 페이지당 30개씩 표시
  for cp in cps[(page - 1) * 30:page * 30]:
    own_account = [{
      'id': oa.username,
      'nickname': oa.first_name,
      'status': 'active'
    } for oa in cp.own_accounts.all()]
    use_accounts = [{
      'id': ua.username,
      'nickname': ua.first_name,
      'status': 'used'
    } for ua in cp.used_account.all()]

    coupons.append({
      'code': cp.code,
      'name': cp.name,
      'image': str(cp.image) if cp.image else None,
      'content': cp.content,
      'required_mileage': cp.required_mileage,
      'expire_at': cp.expire_at,
      'created_at': cp.created_at,
      'status': cp.status,
      'note': cp.note,
      'accounts': own_account + use_accounts,
      'post': {
        'id': cp.post.id,
        'title': cp.post.title,
      }
    })

  return render(request, 'partner/coupon.html', {
    **contexts,
    'post': post, # 여행지 게시글 정보
    'coupons': coupons, # 쿠폰 정보
    'last_page': last_page, # page 처리 작업에 사용(반드시 필요)
  })