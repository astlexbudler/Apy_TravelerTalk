import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect
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
  if account['account_type'] != 'partner':
    return render(request, 'login.html')
  if account['status'] == 'pending':
    return render(request, 'login.html')

  return redirect(settings.PARTNER_URL + '/partner/partner')

# 파트너 관리자 메인 페이지
def index(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.PARTNER_URL)
  account = daos.select_account_detail(request.user.id)
  server_settings = {
      'site_logo': daos.select_server_setting('site_logo'),
      'service_name': daos.select_server_setting('service_name'),
  }
  if account['account_type'] != 'partner' or account['status'] == 'pending':
    return redirect(settings.PARTNER_URL)

  # 게시글 가져오기
  posts = models.POST.objects.select_related(
    'place_info'
  ).prefetch_related(
    'boards', 'place_info__categories'
  ).filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).all()

  # 게시글 정보 포멧
  posts_data = [{
      'id': post.id,
      'author': {
          'id': request.user.id,
          'partner_name': request.user.last_name,
      },
      'place_info': {
          'categories': [{
              'id': c.id,
              'name': c.name,
          } for c in post.place_info.categories.all()],
          'category_ids': ','.join([str(c.id) for c in post.place_info.categories.all()]),
          'location_info': post.place_info.location_info if len(post.place_info.location_info) <= 16 else post.place_info.location_info[:20] + '..',
          'open_info': post.place_info.open_info if len(post.place_info.open_info) <= 16 else post.place_info.open_info[:20] + '..',
          'status': post.place_info.status,
          'ad_start_at': datetime.datetime.strftime(post.place_info.ad_start_at, '%Y-%m-%d') if post.place_info.ad_start_at else None,
          'ad_end_at': datetime.datetime.strftime(post.place_info.ad_end_at, '%Y-%m-%d') if post.place_info.ad_end_at else None,
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
      'search_weight': post.search_weight,
  } for post in posts]

  # 여행지 정보 수정 요청 처리
  if request.method == 'POST':
    for post in posts: # 모든 게시글을 숨김
      daos.update_place_info(
        post_id=post['id'],
        status='writing',
      )
    daos.update_place_info( # 요청한 게시글만 보이게
      post_id=request.GET['post_id'],
      status=request.POST.get('place_status'),
    )
    return JsonResponse({'result': 'success'})

  return render(request, 'partner/index.html', {
    'account': account,
    'server_settings': server_settings,

    'posts': posts_data,
  })

# 새 광고 게시글 작성 페이지*사용하지 않음
def write_post(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.PARTNER_URL)
  account = daos.select_account_detail(request.user.id)
  server_settings = {
      'site_logo': daos.select_server_setting('site_logo'),
      'service_name': daos.select_server_setting('service_name'),
  }
  if account['account_type'] != 'partner' or account['status'] == 'pending':
    return redirect(settings.PARTNER_URL)

  # 게시글 작성 요청
  if request.method == 'POST':
    # 데이터 가져오기
    title = request.POST.get('title')
    content = request.POST.get('content')
    image = request.FILES.get('image')
    board_ids = request.POST.get('board_ids')
    category_ids = request.POST.get('category_ids')
    location_info = request.POST.get('location_info')
    open_info = request.POST.get('open_info')
    address = request.POST.get('address')
    # 게시글 작성
    post = daos.create_post(
      author_id=request.user.id,
      title=title,
      content=content,
      image=image,
      board_ids=board_ids,
    )
    # 게시글의 여행지 정보 작성
    place_info = daos.create_post_place_info(
      post_id=post['pk'],
      location_info=location_info,
      open_info=open_info,
      category_ids=category_ids,
      address=address,
      status='writing',
    )
    # 게시글의 여행지 정보 업데이트
    daos.update_post(
      post_id=post['pk'],
      place_info_id=place_info['pk'],
    )
    return JsonResponse({
      'result': 'success',
      'post_id': post['pk'],
    })

  # data
  boards = daos.make_board_tree(board_type='travel')
  categories = daos.make_category_tree()

  return render(request, 'partner/write_post.html', {
    'account': account,
    'server_settings': server_settings,

    'boards': boards,
    'categories': categories,
  })

# 광고 게시글 수정 페이지
def rewrite_post(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.PARTNER_URL)
  account = daos.select_account_detail(request.user.id)
  server_settings = {
      'site_logo': daos.select_server_setting('site_logo'),
      'service_name': daos.select_server_setting('service_name'),
  }
  if account['account_type'] != 'partner' or account['status'] == 'pending':
    return redirect(settings.PARTNER_URL)

  # 데이터 가져오기
  post_id = request.GET.get('post_id')
  post = daos.select_post(post_id)
  if not post:
    return redirect(settings.PARTNER_URL)

  # 게시글 수정 요청
  if request.method == 'POST':
    # 데이터 가져오기
    title = request.POST.get('title')
    content = request.POST.get('content')
    image = request.FILES.get('image')
    board_ids = request.POST.get('board_ids')
    category_ids = request.POST.get('category_ids')
    location_info = request.POST.get('location_info')
    open_info = request.POST.get('open_info')
    address = request.POST.get('address')
    # 게시글 업데이트
    post = daos.update_post(
      post_id=post_id,
      title=title,
      content=content,
      image=image,
      board_ids=board_ids,
    )
    # 게시글의 여행지 정보 업데이트
    daos.update_place_info(
      post_id=post_id,
      location_info=location_info,
      open_info=open_info,
      category_ids=category_ids,
      address=address,
      status='writing',
    )
    return JsonResponse({
      'result': 'success',
      'post_id': post['pk'],
    })

  # 게시판 및 카테고리 정보
  boards = daos. make_board_tree(board_type='travel')
  categories = daos.make_category_tree()

  return render(request, 'partner/rewrite_post.html', {
    'account': account,
    'server_settings': server_settings,

    'post': post,
    'boards': boards,
    'categories': categories,
  })

# 쿠폰 관리 페이지
def coupon(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.PARTNER_URL)
  account = daos.select_account_detail(request.user.id)
  server_settings = {
      'site_logo': daos.select_server_setting('site_logo'),
      'service_name': daos.select_server_setting('service_name'),
  }
  if account['account_type'] != 'partner' or account['status'] == 'pending':
    return redirect(settings.PARTNER_URL)

  # 데이터 가져오기
  tab = request.GET.get('tab', 'couponTab') # coupopn, history
  page = int(request.GET.get('page', 1))
  search_coupon_code = request.GET.get('code', '') # 쿠폰 이름 검색
  search_coupon_name = request.GET.get('name', '') # 쿠폰 소유자 검색

  # 쿠폰 목록 가져오기
  if tab == 'couponTab': # 쿠폰 목록
    coupons, last_page = daos.select_coupons(
      create_account_id=request.user.id,
      code=search_coupon_code,
      name=search_coupon_name,
      status='active',
      page=page,
    )
  elif tab == 'historyTab': # 쿠폰 사용 내역
    coupons, last_page = daos.select_coupons(
      create_account_id=request.user.id,
      code=search_coupon_code,
      name=search_coupon_name,
      status='history',
      page=page,
    )

  return render(request, 'partner/coupon.html', {
    'account': account,
    'server_settings': server_settings,

    'coupons': coupons,
    'last_page': last_page,
  })

# 프로필
def profile(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.PARTNER_URL)
  account = daos.select_account_detail(request.user.id)
  server_settings = {
      'site_logo': daos.select_server_setting('site_logo'),
      'service_name': daos.select_server_setting('service_name'),
  }
  if account['account_type'] != 'partner' or account['status'] == 'pending':
    return redirect(settings.PARTNER_URL)

  # 데이터 가져오기
  account_id = request.GET.get('account_id', '')
  profile = daos.select_account_detail(account_id)

  return render(request, 'partner/profile.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'profile': profile,
  })

# 활동
def activity(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect(settings.PARTNER_URL)
  account = daos.select_account_detail(request.user.id)
  server_settings = {
      'site_logo': daos.select_server_setting('site_logo'),
      'service_name': daos.select_server_setting('service_name'),
  }
  if account['account_type'] != 'partner' or account['status'] == 'pending':
    return redirect(settings.PARTNER_URL)

  # 데이터 가져오기
  page = int(request.GET.get('page', '1'))
  profile_id = request.GET.get('account_id', '')
  profile = daos.select_account_detail
  activities, last_page = daos.select_account_activities(profile_id, page)
  status = daos.get_account_activity_stats(profile_id)

  return render(request, 'partner/activity.html', {
    **daos.get_urls(),
    'account': account,
    'server_settings': server_settings,

    'profile': profile,
    'status': status,
    'activities': activities,
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
  })
