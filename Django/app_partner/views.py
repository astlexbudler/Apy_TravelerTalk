import datetime
import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout
from django.db.models import Q
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

  return redirect('/partner/partner')

# 파트너 관리자 메인 페이지
def index(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/')
  account = daos.select_account_detail(request.user.id)
  server_settings = {
      'site_logo': daos.select_server_setting('site_logo'),
      'service_name': daos.select_server_setting('service_name'),
  }
  if account['account_type'] != 'partner':
    return redirect('/')

  ps = models.POST.objects.select_related(
    'place_info', 'author'
  ).prefetch_related(
    'boards', 'place_info__categories'
  ).filter(
    author=request.user,
    place_info__isnull=False, # 여행지 정보가 있는 경우
  ).all()
  posts = []
  for post in ps:
    try:
      posts.append({
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

  return render(request, 'partner/index.html', {
    'account': account,
    'server_settings': server_settings,

    'posts': posts,
  })

# 새 광고 게시글 작성 페이지*사용하지 않음
def write_post(request):

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/')
  account = daos.select_account_detail(request.user.id)
  server_settings = {
      'site_logo': daos.select_server_setting('site_logo'),
      'service_name': daos.select_server_setting('service_name'),
  }
  if account['account_type'] != 'partner':
    return redirect('/')

  # 게시글 작성 요청
  if request.method == 'POST':
    print(request.POST.dict())
    post = daos.create_post(
      author_id=request.user.id,
      title=request.POST['title'],
      content=request.POST['content'],
      image=request.FILES.get('image', None),
      board_ids=request.POST['board_ids'],
    )
    place_info = daos.create_post_place_info(
      post_id=post['pk'],
      location_info=request.POST['location_info'],
      open_info=request.POST['open_info'],
      category_ids=request.POST['category_ids'],
      address=request.POST['address'],
      status='writing',
    )
    daos.update_post(
      post_id=post['pk'],
      place_info_id=place_info['pk'],
    )
    return JsonResponse({
      'result': 'success',
      'post_id': post['pk'],
    })

  # data
  boards = daos.make_travel_board_tree()
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
    return redirect('/')
  account = daos.select_account_detail(request.user.id)
  server_settings = {
      'site_logo': daos.select_server_setting('site_logo'),
      'service_name': daos.select_server_setting('service_name'),
  }
  if account['account_type'] != 'partner':
    return redirect('/')

  # 게시글 수정 요청
  if request.method == 'POST':
    print(request.POST.dict())
    post = daos.update_post(
      post_id=request.POST['post_id'],
      title=request.POST['title'],
      content=request.POST['content'],
      image=request.FILES.get('image', None),
      board_ids=request.POST['board_ids'],
    )
    daos.update_place_info(
      post_id=post['pk'],
      location_info=request.POST['location_info'],
      open_info=request.POST['open_info'],
      category_ids=request.POST['category_ids'],
      address=request.POST['address'],
      status='writing',
    )
    return JsonResponse({
      'result': 'success',
      'post_id': post['pk'],
    })

  # 게시글 삭제 요청
  if request.method == 'DELETE':
    post_id = request.GET.get('post_id', None)
    post = daos.select_post(post_id)
    daos.delete_place_info(post['place_info']['id'])
    return JsonResponse({
      'result': 'success',
    })

  # data
  post_id = request.GET.get('post_id', None)
  post = daos.select_post(post_id)
  boards = daos.make_travel_board_tree()
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
    return redirect('/')
  account = daos.select_account_detail(request.user.id)
  server_settings = {
      'site_logo': daos.select_server_setting('site_logo'),
      'service_name': daos.select_server_setting('service_name'),
  }
  if account['account_type'] != 'partner':
    return redirect('/')

  # 데이터 가져오기
  tab = request.GET.get('tab', 'coupon') # coupopn, history
  page = int(request.GET.get('page', 1))
  search_coupon_code = request.GET.get('code', '') # 쿠폰 이름 검색
  search_coupon_name = request.GET.get('name', '') # 쿠폰 소유자 검색

  # 쿠폰 목록 가져오기
  if tab == 'coupon': # 쿠폰 목록
    coupons, last_page = daos.select_owned_coupons(
      account_id=request.user.id,
      status='active',
      page=page,
    )
  elif tab == 'history': # 쿠폰 사용 내역
    coupons, last_page = daos.select_owned_coupons(
      account_id=request.user.id,
      page=page,
    )

  return render(request, 'partner/coupon.html', {
    'account': account,
    'server_settings': server_settings,

    'coupons': coupons,
    'last_page': last_page,
  })