from django.shortcuts import redirect, render
from app_core import daos



# 메인 페이지
def index(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  page = int(request.GET.get('page', '1'))

  # 메인 페에지에 표시할 여행지 게시글 가져오기
  posts, last_page = daos.select_posts(
    post_type='ad',
    page=page,
  )

  # 배너 정보 가져오기
  banners = {
    'top': daos.select_banners('top'),
    'side': daos.select_banners('side'),
  }

  return render(request, 'index.html', {
    **contexts,
    'boards': boards, # 게시판 정보

    'banners': banners, # 배너 정보
    'posts': posts, # 여행지 게시글 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
  })

# 회원가입 페이지
def signup(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 리다이렉트
  if contexts['account']['account_type'] != 'guest':
    return redirect('/?redirect_message=already_login')

  # 파트너 계정 생성을 위한 게시판 및 카테고리 정보
  travel_boards = daos.make_board_tree(board_type='travel')
  categories = daos.make_category_tree()

  return render(request, 'signup.html', {
    **contexts,
    'boards': boards, # 게시판 정보

    'travel_boards': travel_boards, # 여행지 게시판 정보
    'categories': categories, # 카테고리 정보
  })

# 프로필 페이지
def profile(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 리다이렉트
  if contexts['account']['account_type'] == 'guest':
    return redirect('/?redirect_message=need_login')

  # 프로필 정보 가져오기
  profile = daos.select_account_detail(contexts['account']['id'])

  # 레벨 규칙 정보
  level_rules = daos.select_all_levels()

  return render(request, 'profile.html', {
    **contexts,
    'boards': boards, # 게시판 정보

    'profile': profile, # 사용자 또는 profile_id에 해당하는 사용자의 프로필 정보
    'level_rules': level_rules, # 사용자의 레벨 규칙 정보
  })

# 활동 페이지
def activity(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 리다이렉트
  if contexts['account']['account_type'] == 'guest':
    return redirect('/?redirect_message=need_login')

  # data
  page = int(request.GET.get('page', '1'))

  # 프로필 정보도 같이 가져옴
  profile = daos.select_account_detail(contexts['account']['id'])

  # 프로필의 활동 내역 가져오기
  activities, last_page = daos.select_account_activities(contexts['account']['id'], page)

  # 활동 내역 요약 정보
  status = daos.get_account_activity_stats(contexts['account']['id'])

  return render(request, 'activity.html', {
    **contexts, # 기본 컨텍스트 정보
    'boards': boards, # 게시판 정보

    'profile': profile, # 사용자 또는 profile_id에 해당하는 사용자의 프로필 정보
    'status': status, # 활동 내역 요약 정보
    'activities': activities, # 사용자 또는 profile_id에 해당하는 사용자의 활동 내역
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
  })

# 북마크 페이지
def bookmark(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 리다이렉트
  if contexts['account']['account_type'] == 'guest':
    return redirect('/?redirect_message=need_login')

  # 사용자의 북마크 정보 가져오기(여행지 게시글만 북마크 가능)
  bookmarks = daos.select_account_bookmarked_posts(contexts['account']['id'])

  return render(request, 'bookmark.html', {
    **contexts, # 기본 컨텍스트 정보
    'boards': boards, # 게시판 정보

    'bookmarks': bookmarks, # 사용자의 북마크 정보
  })

# 이용약관 페이지
def terms(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 이용약관 본문 가져오기
  terms = daos.select_server_setting('terms')

  return render(request, 'terms.html', {
    **contexts, # 기본 컨텍스트 정보
    'boards': boards, # 게시판 정보

    'terms': terms, # 이용약관 본문
  })
