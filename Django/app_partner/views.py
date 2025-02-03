from datetime import datetime
import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, get_user_model
from django.db.models import Q

from app_core import models
from app_core import daos

# 파트너 관리자 메인 페이지
def index(request):
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
    return redirect('/?redirect_message=need_login') # 로그인 필요 메세지 표시
  if account_type != 'partner': # 파트너 계정이 아닌 경우
    return redirect('/?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 사용자 프로필 정보
  profile = daos.get_user_profile_by_id(contexts['account']['id'])

  # 파트너 계정이 소유한 여행지 게시글
  p = models.POST.objects.filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).first()
  if not p: # 여행지 게시글이 없는 경우, 광고 게시글 작성 페이지로 이동
    return redirect('/partner/write_post?redirect_message=need_travel_post')
  post = daos.get_post_info(p.id)

  return render(request, 'partner/index.html', {
    **contexts,
    'profile': profile, # 사용자 프로필 정보
    'post': post, # 여행지 게시글 정보
  })

# 새 광고 게시글 작성 페이지
def write_post(request):
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
    return redirect('/?redirect_message=need_login') # 로그인 필요 메세지 표시
  if account_type != 'partner': # 파트너 계정이 아닌 경우
    return redirect('/?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 로그인 여부 확인
  if not request.user.is_authenticated: # 로그인이 되어 있지 않은 경우
    return redirect('/?redirect_message=need_login') # 로그인 페이지로 리다이렉트
  # 파트너 계정 확인
  if 'partner' not in contexts['account']['groups']: # 파트너 계정이 아닌 경우
    return redirect('/?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 광고 게시글이 이미 있는 경우, 광고 게시글 수정 페이지로 이동
  p = models.POST.objects.filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).first()
  if p: # 여행지 게시글이 있는 경우
    return redirect('/partner/rewrite_post?redirect_message=travel_post_exist')

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
    return redirect('/?redirect_message=need_login') # 로그인 필요 메세지 표시
  if account_type != 'partner': # 파트너 계정이 아닌 경우
    return redirect('/?redirect_message=partner_status_error') # 홈으로 리다이렉트
  if 'partner' not in contexts['account']['groups']: # 파트너 계정이 아닌 경우
    return redirect('/?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 광고 게시글 정보
  p = models.POST.objects.filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).first()
  if not p: # 여행지 게시글이 없는 경우, 광고 게시글 작성 페이지로 이동
    return redirect('/partner/write_post?redirect_message=need_travel_post')
  post = daos.get_post_info(p.id)

  # 광고 게시글 작성지 확인
  if contexts['account']['id'] != post['author']['id']:  # 광고 게시글 작성자가 아닌 경우
    return redirect('/?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 광고 게시글 수정
  # title, content, images, board_id 수정 가능
  '''
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
  '''

  # 게시판 정보
  boards = daos.get_board_tree(account_type)

  # 카테고리 정보
  categories = daos.get_category_tree()

  return render(request, 'partner/rewrite_post.html', {
    **contexts,
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
    return redirect('/?redirect_message=need_login') # 로그인 필요 메세지 표시
  if account_type != 'partner': # 파트너 계정이 아닌 경우
    return redirect('/?redirect_message=partner_status_error') # 홈으로 리다이렉트

  # 여행지 게시글
  p = models.POST.objects.filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).first()
  if not p: # 여행지 게시글이 없는 경우, 광고 게시글 작성 페이지로 이동
    return redirect('/partner/write_post?redirect_message=need_travel_post')
  post = daos.get_post_info(p.id)

  # 새 쿠폰 생성
  '''
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
  '''

  # 데이터 가져오기
  page = int(request.GET.get('page', 1))
  search_coupon_name = request.GET.get('search_coupon_name', '') # 쿠폰 이름 검색
  search_coupon_status = request.GET.get('search_coupon_status', '') # 쿠폰 상태 검색
  search_coupon_owner = request.GET.get('search_coupon_owner', '') # 쿠폰 소유자 검색

  # 쿠폰 목록 가져오기
  cps = models.COUPON.objects.prefetch_related('own_accounts').filter(
    create_account=request.user,
    name__contains=search_coupon_name,
    status__contains=search_coupon_status,
    own_accounts__id__in=search_coupon_owner,
  ).order_by('-expire_at')
  coupons = []
  last_page = len(cps) // 30 + 1 # 한 페이지당 30개씩 표시
  for cp in cps[(page - 1) * 30:page * 30]:
    coupons.append({
      'code': cp.code,
      'name': cp.name,
      'image': cp.image,
      'content': cp.content,
      'required_point': cp.required_point,
      'expire_at': cp.expire_at,
      'created_at': cp.created_at,
      'status': cp.status,
      'note': cp.note,
      'own_accounts': [{
        'id': oa.username,
        'nickname': oa.first_name,
      } for oa in cp.own_accounts],
    })

  return render(request, 'partner/coupon.html', {
    **contexts,
    'post': post, # 여행지 게시글 정보
    'coupons': coupons, # 쿠폰 정보
    'last_page': last_page, # page 처리 작업에 사용(반드시 필요)
  })