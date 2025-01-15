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

from app_post import daos as post_do
from app_core import daos as core_do
from app_user import daos as user_do
from app_message import daos as message_do
from app_coupon import daos as coupon_do
from app_partner import daos as partner_do

# 기본 컨텍스트
# server, account, messages, coupons, boards, best_reviews, activities
def get_default_context(request):

  # 사용자 프로필 정보 가져오기
  # 로그인하지 않은 사용자는 guest로 처리
  account = user_do.get_user_profile(request)

  # 읽지 않는 쪽지 미리보기
  # 관리자의 경우 수신자가 'supervisor'인 쪽지로 검색해서 가져옴
  messages = message_do.get_user_message_previews(request)

  # 사용자가 가진 쿠폰 미리보기
  # 파트너의 경우, 파트너가 생성한 쿠폰들 미리보기
  coupons = coupon_do.get_user_coupon_previews(request)

  # 서버 설정 가져오기
  server = core_do.get_server_settings()

  # 게시판 트리 가져오기
  # 게시판 트리는 최대 4단계까지 구성됨.
  boards = post_do.get_boards()

  # 베스트 리뷰 가져오기
  # 기간 상관 없이 가장 weight가 높은 상위 5개 리뷰 게시글 정보
  best_reviews = post_do.get_best_review_preview()

  # 사용자 활동 내역
  # 로그인 되어 있는 경우에만 활동 내역을 가져옴.
  activities = user_do.get_account_activitie_preview(account)

  return {
    'server': server,
    'account': account,
    'messages': messages,
    'coupons': coupons,
    'boards': boards,
    'activities': activities,
    'best_reviews': best_reviews,
  }

# 메인 페이지
def index(request):
  context = get_default_context(request)

  # data
  page = int(request.GET.get('page', '1'))

  # 배너 정보 가져오기
  # 현재 배너는 메인 페이지에만 표시됨,
  bs = supervisor_mo.BANNER.objects.all().order_by('display_order')
  banners = {
    'top': [], # 상단 배너
    'side': [], # 사이드 및 하단 배너
  }
  for b in bs:
    if b.location == 'top':
      banners['top'].append({
        'id': b.id,
        'image': b.image,
        'link': b.link,
      })
    elif b.location == 'side':
      banners['side'].append({
        'id': b.id,
        'image': b.image,
        'link': b.link,
      })

  # 메인 페에지에 표시할 여행지 게시글 가져오기
  travel_posts = []
  all_ads = post_mo.AD.objects.filter(
    Q(status='active') | Q(status='expired') # status는 여행지 게시글의 '베스트 업체' 뱃지 표시 여부 결정
  ).order_by('status', '-weight') # weight 광고 정책에서 관리자가 수정 가능.
  last_page = all_ads.count() // 20 + 1 # 페이지당 20개씩 표시

  # 여행지 게시글 정보 가져오기
  for ad in all_ads[(page-1)*20:page*20]:
    # 광고 게시글 정보 가져오기
    if not ad.post_id:
      continue

    po = post_mo.POST.objects.filter(
      id=ad.post_id
    ).first()
    if not po:
      continue

    # 광고 게시글 작성자 정보 가져오기
    po_author = get_user_model().objects.filter(
      status='active',
      username=po.author_id
    ).first()
    if not po_author:
      continue
    author = {
      'id': po_author.username,
      'nickname': po_author.first_name,
      'account_type': po_author.account_type,
      'status': po_author.status,
      'partner_categories': po_author.partner_categories,
      'partner_address': po_author.partner_address,
    }

    # 광고 게시글이 속한 게시판 정보
    boards = []
    for b in str(po.board_id).split(','):
      if not b:
        continue
      board = post_mo.BOARD.objects.get(id=b)
      boards.append({
        'id': board.id,
        'name': board.name,
      })

    # 광고 게시글
    travel_posts.append({
      'ad_id': ad.id,
      'status': ad.status,
      'id': po.id,
      'title': po.title,
      'boards': boards,
      'author': author,
      'created_dt': po.created_dt,
      'image': str(po.images).split(',')[0],
      'view_count': len(str(po.views).split(',')) - 1,
      'like_count': len(str(po.bookmarks).split(',')) - 1,
      'comment_count': post_mo.COMMENT.objects.filter(post_id=po.id).count(),
    })

  return render(request, 'index.html', {
    **context,
    'banners': banners,
    'travel_posts': travel_posts,
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
  })

# 회원가입 페이지
def signup(request):
  context = get_default_context(request)
  # 이미 로그인되 경우, 리다이렉트 후 메세지 표시
  if context['account']['account_type'] != 'guest':
    return redirect('/?redirect=already_login')

  # 카테고리 정보(파트너 가입 시 필요)
  categories = partner_do.get_categories()

  return render(request, 'signup.html', {
    **context,
    'categories': categories,
  })

# 계정 찾기 페이지
# 계정 찾기는 관리자 문의를 통해 가능함
def find_account(request):
  context = get_default_context(request)
  # 이미 로그인되 경우, 리다이렉트 후 메세지 표시
  if context['account']['account_type'] != 'guest':
    return redirect('/?redirect=already_login')

  return render(request, 'find_account.html', context)

# 프로필 페이지
# 관릐자의 경우, 다른 계정의 프로필 조회 가능.
def profile(request):
  context = get_default_context(request)
  # 로그인 되지 않은 경우, 리다이렉트 후 로그인 필요 메세지 표시
  if context['account']['status'] == 'guest':
    return redirect('/?redirect=need_login')

  # data
  # 최상위 관리자 또는 사용자 권한이 있는 부관리자 계정일 경우, 다른 사용자의 프로필 페이지 접근 가능
  if context['account']['account_type'] == 'supervisor' or (context['account']['account_type'] == 'sub_supervisor' and 'user' in context['account']['supervisor_permissions']):
    profile_id = request.GET.get('profile_id', request.user.username)
  else: # 그 외의 경우, 자신의 프로필 페이지만 접근 가능
    profile_id = request.user.username

  # 프로필 정보 가져오기
  profile = user_do.get_user_profile_by_id(profile_id)

  # 레벨 규칙 정보
  # 사용자만 레벨 규칙 정보를 가져옴
  level_rules = core_do.get_level_rules() if profile['account_type'] == 'user' or profile['account_type'] == 'dame' else None

  # 카테고리 정보
  # 파트너만 카테고리 정보를 가져옴
  categories = partner_do.get_categories() if profile['account_type'] == 'partner' else None

  return render(request, 'profile.html', {
    **context,
    'profile': profile, # 사용자 또는 profile_id에 해당하는 사용자의 프로필 정보
    'level_rules': level_rules,
    'categories': categories, # 파트너의 카테고리 정보 수정에 필요.
  })

# 활동 페이지
# 관리자와 파트너는 다른 사용자의 활동 페이지를 조회 가능.
def activity(request):
  context = get_default_context(request)
  # 로그인 되지 않은 경우, 리다이렉트 후 로그인 필요 메세지 표시
  if context['account']['status'] == 'guest':
    return redirect('/?redirect=need_login')

  # data
  page = int(request.GET.get('page', '1'))
  # 관리자 또는 파트너 확인 가능
  if request.GET.get('profile_id') and ('supervisor' in context['account']['account_type'] or context['account']['account_type'] == 'partner'):
    profile_id = request.GET.get('profile_id')
  else: # 그 외의 경우, 자신의 활동 페이지만 접근 가능
    profile_id = request.user.username

  print(profile_id)

  # 프로필 정보도 같이 가져옴
  profile = user_do.get_user_profile_by_id(profile_id)

  # 프로필의 활동 내역 가져오기
  acts = user_do.get_user_activities(profile_id, page)
  activities = acts['activities']
  last_page = acts['last_page']

  return render(request, 'activity.html', {
    **context,
    'profile': profile, # 사용자 또는 profile_id에 해당하는 사용자의 프로필 정보
    'activities': activities, # 사용자 또는 profile_id에 해당하는 사용자의 활동 내역
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
  })

# 북마크 페이지
def bookmark(request):
  context = get_default_context(request)
  # 로그인 되지 않은 경우, 리다이렉트 후 로그인 필요 메세지 표시
  if context['account']['status'] == 'guest':
    return redirect('/?redirect=need_login')

  # 이미 context.account.bookmakrs에 저장된 북마크 게시글 정보가 포함됨.

  return render(request, 'bookmark.html', context)

# 제휴 문의 페이지
def contact(request):
  context = get_default_context(request)

  # 쪽지 발송은, api/send_message를 통해서 가능.

  return render(request, 'contact.html', context)

# 이용약관 페이지
def terms(request):
  context = get_default_context(request)

  # 이용약관 본문 가져오기
  terms = core_mo.SERVER_SETTING.objects.get(id='terms').value

  return render(request, 'terms.html', {
    **context,
    'terms': terms,
  })




