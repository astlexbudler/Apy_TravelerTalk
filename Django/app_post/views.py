import datetime
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


# 게시판 페이지
# 이 페이지는 아래와 같은 경우로 나뉨
# 1. 특정 게시판으로 이동을 요청하는 경우 => 해당 게시판으로 redirect
# 2. 전체 글 검색을 하는 경우(board_id 가 없음) => 전체 게시글 검색
# 3. 사전 정의되지 않은 기타 게시판의 경우 => 해당 게시글 검색
def index(request):
  context = get_default_context(request)

  # data
  board_ids = request.GET.get('board_ids', '') # 전체 글 검색의 경우 board_id가 없음
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')

  # board 확인
  # 게시판의 접근 권한 및 사전 게시판 확인은 마지막 게시판만 확인하면 됨.
  boards = []
  for board_id in board_ids.split(','):
    if board_id == '':
      continue
    board = post_mo.BOARD.objects.filter(id=board_id).first()
    if board:
      boards.append({
        'id': board.id,
        'name': board.name,
        'post_type': board.post_type,
        'display_permissions': board.display_permissions,
        'enter_permissions': board.enter_permissions,
        'write_permissions': board.write_permissions,
        'comment_permissions': board.comment_permissions,
      })

  if boards != []: # 게시판이 있을 경우,

    # 게시판이 사전 정의된 게시판인지 확인
    if boards[-1]['post_type'] == 'event': # 이벤트 게시판
      return redirect('/post/event')
    elif boards[-1]['post_type'] == 'notice': # 공지사항 게시판
      return redirect('/post/notice')
    elif boards[-1]['post_type'] == 'attendance': # 출석체크 게시판
      return redirect('/post/attendance')
    elif boards[-1]['post_type'] == 'greeting': # 가입인사 게시판
      return redirect('/post/greeting')
    elif boards[-1]['post_type'] == 'review': # 리뷰 게시판
      return redirect('/post/review')
    elif boards[-1]['post_type'] == 'travel': # 여행 게시판
      return redirect('/post/travel?board_ids=' + board_ids)

    # 게시판 접근 권한 확인, 게시판 표시 권한 확인(display_permissions)
    account_type = context['account']['account_type']
    if 'dame' == account_type and 'pending' == context['account']['status']:
      account_type = 'user' # 가입 승인 대기중인 여성 회원은 user 권한을 가짐
    if account_type not in boards[-1]['display_permissions']:
      return redirect('/?redirect=not_allowed_board')

  # 게시글 정보 확인
  # 시스템에서 작성한 게시글은 제외
  board_ids = str(board_ids).split(',')
  if board_ids == ['']:
    pts = post_mo.POST.objects.exclude(
      author_id='system'
    ).filter(
      title__contains=search, # search가 없는 경우, 전체 글 검색
    ).order_by('-created_dt')
    boards = [{
      'id': 'all',
      'name': '전체',
    }]
  else:
    pts = post_mo.POST.objects.exclude(
      author_id = 'system'
    ).filter(
      Q(board_id__contains=board_ids[-1]) & Q(title__contains=search) # search가 없는 경우, 전체 글 검색
    ).order_by('-created_dt')
  last_page = len(pts) // 20 + 1 # 한 페이지당 20개씩 표시
  posts = post_do.get_post_search(pts[20 * (page - 1):20 * page])

  return render(request, 'post/index.html', {
    **context,
    'board': boards[-1],
    'posts': posts,
    'last_page': last_page,
  })

# 게시글 작성 페이지
def write_post(request):
  context = get_default_context(request)
  if context['account']['status'] == 'guest': # 게스트는 게시글 작성 불가
    return redirect('/?redirect=need_login')

  # board 확인
  board_ids = request.GET.get('board_ids', '')
  post_boards = []
  for board_id in board_ids.split(','):
    if board_id == '':
      continue
    board = post_mo.BOARD.objects.filter(id=board_id).first()
    if board:
      post_boards.append({
        'id': board.id,
        'name': board.name,
        'write_permissions': board.write_permissions,
      })
  account_type = context['account']['account_type']
  if 'dame' == account_type and 'pending' == context['account']['status']:
    account_type = 'user'

  # 게시판 글 작성 권한 확인
  if post_boards == []: # 게시판이 없는 경우
    return redirect('/?redirect=not_found_board')
  # 게시글 작성 권한이 없음
  if account_type not in post_boards[-1]['write_permissions']:
    return redirect('/?redirect=not_allowed_board')

  # 게시글 작성 처리 요청
  if request.method == 'POST':
    title = request.POST.get('title')
    content = request.POST.get('content')
    if not title or not content: # 제목 또는 내용이 없는 경우
      return JsonResponse({'result': 'error'})
    post = post_mo.POST(
      board_id=board_ids,
      author_id=context['account']['id'],
      title=title,
      content=content,
    )
    post.save()

    # 사용자 활동 기록 추가
    # 사용자 계정 및 파트너 계정만 해당
    if any(context['account']['account_type'] in s for s in ['user', 'dame', 'partner']):
      point = core_mo.SERVER_SETTING.objects.get(id='post_point').value
      # point_change는 사용자 계정일때만 적용
      act = user_mo.ACTIVITY(
        user_id=context['account']['id'],
        location='/post/post_view?post=' + str(post.id),
        message=f'{post_boards[-1]["name"]} 게시글 작성. ({title})',
        point_change=f'+{point}' if context["account"]["account_type"] != "partner" else "",
      )
      act.save()
      # 사용자 계정일 경우, 포인트 증가
      if context['account']['account_type'] == 'user' or context['account']['account_type'] == 'dame':
        account = get_user_model().objects.get(username=context['account']['id'])
        account.user_level_point += point
        account.user_usable_point += point
        account.save()

    return JsonResponse({'result': 'success', 'post_id': post.id})

  return render(request, 'post/write_post.html', {
    **context,
  })

# 게시글 수정 페이지
def rewrite_post(request):
  context = get_default_context(request)

  # data
  post_id = request.GET.get('post', '')

  # post 확인
  po = post_mo.POST.objects.filter(id=post_id).first()
  if not po: # 게시글이 존재하지 않는 경우
    return redirect('/?redirect=not_found_post')
  if context['account']['id'] != po.author_id: # 사용자와 작성자가 다른 경우
    # 관리자의 경우(게시글 권한이 있는) 게시글 수정 가능
    if context['account']['account_type'] == 'supervisor' or (context['account']['account_type'] == 'sub_supervisor' and 'post' in context['account']['supervisor_permissions']):
      pass
    return redirect('/?redirect=not_allowed')

  # 게시글의 게시판 정보
  bos = str(po.board_id).split(',')
  boards = []
  for bo in bos:
    board = post_mo.BOARD.objects.filter(id=bo).first()
    if board:
      boards.append({
        'id': bo,
        'name': board.name,
      })

  # 게시글 수정 요청
  if request.method == 'POST':
    title = request.POST.get('title', po.title)
    content = request.POST.get('content', po.content)
    if not title or not content:
      return JsonResponse({'result': 'error'})
    po.title = title
    po.content = content
    po.save()

    # 사용자 활동 기록 추가
    # 사용자 계정 및 파트너 계정만 해당
    if any(context['account']['account_type'] in s for s in ['user', 'dame', 'partner']):
      act = user_mo.ACTIVITY(
        user_id=context['account']['id'],
        location='/post/post_view?post=' + post_id,
        message=f'[{boards[-1]["name"]}] 게시글 수정. ({title})',
        point_change='0',
      )
      act.save()

    return JsonResponse({'result': 'success'})

  # 게시글 정보
  post = {
    'id': po.id,
    'boards': boards,
    'title': po.title,
    'content': po.content
  }

  return render(request, 'post/rewrite_post.html', {
    **context,
    'post': post,
  })

# 게시글 상세 페이지
def post_view(request):
  context = get_default_context(request)

  # data
  post_id = request.GET.get('post', '')

  # search
  po = post_mo.POST.objects.filter(id=post_id).first()
  if not po: # 게시글이 존재하지 않는 경우
    return redirect('/?redirect=not_found_post')

  # board
  bos = str(po.board_id).split(',')
  boards = []
  for bo in bos:
    if bo != '':
      board = post_mo.BOARD.objects.filter(id=bo).first()
      boards.append({
        'id': bo,
        'name': board.name,
        'enter_permissions': board.enter_permissions,
      })

  # 게시글 확인 권한 확인
  # 최 하단 게시판의 게시글 접근 권한 확인(enter_permissions)
  last_board = boards[-1]
  if context['account']['account_type'] == 'dame' and context['account']['status'] == 'pending':
    account_type = 'user'
  else:
    account_type = context['account']['account_type']
  if account_type not in last_board['enter_permissions']:
    return redirect('/?redirect=not_allowed_board')

  # author
  at = get_user_model().objects.filter(
    username=po.author_id
  ).first()

  # 게시글 작성자가 사용자일 경우
  if any(at.account_type in s for s in ['user', 'dame']):

    # 레벨
    lv = core_mo.LEVEL_RULE.objects.get(level=at.user_level)
    level = {
      'level': lv.level,
      'text_color': lv.text_color,
      'background_color': lv.background_color,
      'name': lv.name,
    }

    # 게시글 작성자 정보
    author = {
      'id': po.author_id,
      'nickname': at.first_name,
      'level': level,
      'account_type': at.account_type,
      'status': at.status,
    }

  # 게시글 작성자가 파트너일 경우
  elif at.account_type == 'partner':

    author = {
      'id': po.author_id,
      'nickname': at.first_name,
      'account_type': at.account_type,
      'status': at.status,
      'partner_address': at.partner_address,
      'partner_categories': at.partner_categories,
    }

  # post
  post = {
    'id': po.id,
    'author': author,
    'boards': boards,
    'title': po.title,
    'content': po.content,
    'created_dt': po.created_dt,
    'views': str(po.views).split(','),
    'bookmarks': str(po.bookmarks).split(','),
  }

  # Comments
  comments = post_do.get_post_comments(post_id)

  # 조회수 증가
  if not context['account']['id'] in po.views:
    po.views += ',' + context['account']['id']
    po.save()
    post['views'].append(context['account']['id'])

  return render(request, 'post/post_view.html', {
    **context,
    'post': post,
    'comments': comments,
  })

# 공지사항 페이지
def notice(request):
  context = get_default_context(request)

  # board
  bo = post_mo.BOARD.objects.filter(post_type='notice').first()
  board = {
    'id': bo.id,
    'name': bo.name,
  }

  # 공지사항 가져오기
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')
  pos = post_mo.POST.objects.filter(
    board_id=bo.id,
    title__contains=search,
  ).order_by('-created_dt')
  last_page = len(pos) // 20 + 1 # 한 페이지당 20개씩 표시
  posts = []
  for po in pos[20 * (page - 1):20 * page]:
    # 어차피 공지사항은 관리자가 작성한 글이므로, 작성자 정보 pass
    posts.append({
      'id': po.id,
      'title': po.title,
      'created_dt': po.created_dt,
      'view_count': len(str(po.views).split(',')) - 1,
      'bookmark_count': len(str(po.bookmarks).split(',')) - 1,
      'comment_count': post_mo.COMMENT.objects.filter(post_id=po.id).count(),
    })

  return render(request, 'post/notice.html', {
    **context,
    'board': board,
    'posts': posts,
    'last_page': last_page,
  })

# 이벤트 게시판 페이지
def event(request):
  context = get_default_context(request)

  # board
  bo = post_mo.BOARD.objects.filter(post_type='event').first()

  # 이벤트 가져오기
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')
  pos = post_mo.POST.objects.filter(
    board_id=bo.id,
    title__contains=search,
  ).order_by('-created_dt')
  last_page = len(pos) // 20 + 1
  posts = []
  for po in pos[20 * (page - 1):20 * page]:
    # 이벤트 게시글도 마찬가지로 관리자가 작성한 글이므로, 작성자 정보 pass
    posts.append({
      'id': po.id,
      'title': po.title,
      'created_dt': po.created_dt,
      'view_count': len(str(po.views).split(',')) - 1,
      'bookmark_count': len(str(po.bookmarks).split(',')) - 1,
      'comment_count': post_mo.COMMENT.objects.filter(post_id=po.id).count(),
      'images': str(po.images).split(','), # 이미지는 최대 1개
    })

  return render(request, 'post/event.html', {
    **context,
    'posts': posts,
    'last_page': last_page,
  })

# 이벤트 게시글 작성
def write_event(request):
  context = get_default_context(request)

  # 권한 확인
  if context['account']['account_type'] == 'supervisor' or (context['account']['account_type'] != 'sub_supervisor' and 'post' in get_user_model().objects.get(username=context['account']['id']).supervisor_permissions):
    # 관리자이거나 부관리자의 경우 post 권한이 있는 경우만 통과
    pass
  else:
    return redirect('/?redirect=not_allowed')

  # board
  bo = post_mo.BOARD.objects.filter(post_type='event').first()
  board = {
    'id': bo.id,
    'name': bo.name,
  }

  # 이벤트 작성
  if request.method == 'POST':
    title = request.POST.get('title', '')
    content = request.POST.get('content', '')
    images = request.POST.get('image', '')
    po = post_mo.POST(
      board_id=bo.id,
      author_id=context['account']['id'],
      title=title,
      content=content,
      images=images,
    )
    po.save()
    return JsonResponse({'result': 'success'})

  return render(request, 'post/write_event.html', {
    **context,
    'board': board,
  })

# 이벤트 게시글 수정
def rewrite_event(request):
  context = get_default_context(request)

  # 권한 확인
  if context['account']['account_type'] == 'supervisor' or (context['account']['account_type'] != 'sub_supervisor' and 'post' in get_user_model().objects.get(username=context['account']['id']).supervisor_permissions):
    # 관리자이거나 부관리자의 경우 post 권한이 있는 경우만 통과
    pass
  else:
    return redirect('/?redirect=not_allowed')

  # 이벤트 게시글 가져오기
  post_id = request.GET.get('post', '')
  po = post_mo.POST.objects.filter(id=post_id).first()
  if not po:
    return redirect('/?redirect=not_found_post')
  post = {
    'id': po.id,
    'title': po.title,
    'content': po.content,
    'images': po.images,
  }

  # 이벤트 게시글 수정
  if request.method == 'POST':
    title = request.POST.get('title', po.title)
    content = request.POST.get('content', po.content)
    images = request.POST.get('image', po.images)
    po.title = title
    po.content = content
    po.images = images
    po.save()

    return JsonResponse({
      'result': 'success',
      'post_id': po.id,
    })

  return render(request, 'post/rewrite_event.html', {
    **context,
    'post': post,
  })

# 이벤트 게시글 상세
def event_view(request):
  context = get_default_context(request)

  # data
  post_id = request.GET.get('post', '')

  # 이벤트 게시글 확인
  po = post_mo.POST.objects.filter(id=post_id).first()
  if not po:
    return redirect('/?redirect=not_found_post')

  # board
  bo = post_mo.BOARD.objects.filter(id=po.board_id).first()
  if not bo:
    return redirect('/?redirect=not_found_board')
  elif bo.post_type != 'event':
    return redirect('/?redirect=not_allowed_board')

  # post
  post = {
    'id': po.id,
    'title': po.title,
    'content': po.content,
    'images': str(po.images).split(',')[0],
    'created_dt': po.created_dt,
    'views': str(po.views).split(','),
    'bookmarks': str(po.bookmarks).split(','),
  }

  # comments
  comments = post_do.get_post_comments(post_id)

  # 조회수 증가
  if not context['account']['id'] in po.views:
    po.views += ',' + context['account']['id']
    po.save()
    post['views'].append(context['account']['id'])

  return render(request, 'post/event_view.html', {
    **context,
    'post': post,
    'comments': comments,
  })

# 출석체크 게시판
def attendance(request):
  context = get_default_context(request)

  # 권한 확인
  if context['account']['account_type'] == 'guest':
    # 게스트는 출석체크 게시판 접근 불가
    return redirect('/?redirect=need_login')

  # board
  bo = post_mo.BOARD.objects.filter(post_type='attendance').first()
  board = {
    'id': bo.id,
    'name': bo.name,
  }

  # 출석 체크 게시플 가져오기
  # 춣석체크는 오늘 날짜의 출석체크 게시글에 댓글을 다는걸로 구현됨.
  today = datetime.datetime.now().strftime('%Y-%m-%d')
  post = post_mo.POST.objects.filter(
    board_id=bo.id,
    title=f'출석체크:{today}',
  ).first()
  if not post: # 만약 오늘의 출석체크 게시긇이 없다면, 생성
    post = post_mo.POST(
      board_id=bo.id,
      author_id='system',
      title=f'출석체크:{today}',
      content='',
    )
    post.save()
  today_post = {
    'id': post.id,
  }

  # 출석체크 댓글 작성 요청 처리
  if request.method == 'POST':
    content = request.POST.get('content', '')
    if not content:
      return JsonResponse({'result': 'error'})

    # 이미 출석을 했는지 확인
    if post_mo.COMMENT.objects.filter(
      post_id=post.id,
      author_id=context['account']['id'],
    ).exists():
      return JsonResponse({'result': 'error'})

    # 오늘의 출석체크 등수 확인
    comment_length = post_mo.COMMENT.objects.filter(
      post_id=post.id,
    ).count()
    if comment_length == 0: # 첫 댓글인 경우
      point = int(core_mo.SERVER_SETTING.objects.get(id='attend_point').value) * 2
    elif comment_length == 1: # 두 번째 댓글인 경우
      point = int(core_mo.SERVER_SETTING.objects.get(id='attend_point').value) * 1.5
    elif comment_length == 2: # 세 번째 댓글인 경우
      point = int(core_mo.SERVER_SETTING.objects.get(id='attend_point').value) * 1.2
    else: # 네 번째 댓글 이상인 경우
      point = int(core_mo.SERVER_SETTING.objects.get(id='attend_point').value)

    # 출석체크 댓글 작성
    comment = post_mo.COMMENT(
      post_id=post.id,
      author_id=context['account']['id'],
      content=content,
    )
    comment.save()

    # 사용자 활동 기록 추가 및 포인트 증가
    # 사용자 계정 및 파트너 계정만 해당
    if context['account']['account_type'] in ['user', 'dame', 'partner']:
      act = user_mo.ACTIVITY(
        user_id=context['account']['id'],
        location='/post/attendance',
        message=f'출석체크 댓글 작성',
        point_change=point,
      )
      act.save()

      # 사용자 계정일 경우, 포인트 증가
      account = get_user_model().objects.get(username=context['account']['id'])
      account.user_level_point += point
      account.user_usable_point += point
      account.save()

    return JsonResponse({'result': 'success'})

  # 오늘의 출석 댓글 가져오기
  comments = post_do.get_post_comments(post.id)

  # 사용자가 이전에 출석한 날짜 가져오기
  is_attended = False
  attend_days = []
  monthPosts = post_mo.POST.objects.filter(
    board_id=bo.id,
    title__contains=f'출석체크:{datetime.datetime.now().strftime("%Y-%m")}', # 이번달 출석체크 게시글
  ).order_by('-created_dt')
  for post in monthPosts:
    attend = post_mo.COMMENT.objects.filter(
      post_id=post.id,
      author_id=context['account']['id'],
    ).first()
    if attend: # 출석 댓글이 있는 경우,
      attend_days.append(int(post.title.split('-')[-1])) # 출석 체크한 날짜 추가
      if attend.created_dt.strftime('%Y-%m-%d') == datetime.datetime.now().strftime('%Y-%m-%d'):
        is_attended = True

  return render(request, 'post/attendance.html', {
    **context,
    'comments': comments, # 출석 체크 글
    'post': today_post, # 오늘의 출석체크 게시글 아이디
    'attend_days': attend_days, # 사용자가 출석체크한 날짜
    'is_attended': is_attended, # 오늘 출석체크를 했는지 여부
  })

# 가입인사 게시판
def greeting(request):
  context = get_default_context(request)

  # 권한 확인
  if context['account']['account_type'] == 'guest':
    # 게스트는 가입인사 게시판 접근 불가
    return redirect('/?redirect=need_login')

  # board
  board = post_mo.BOARD.objects.filter(post_type='greeting').first()
  if not board:
    return redirect('/?redirect=not_found_board')

  # 가입인사 게시글 가져오기
  post = post_mo.POST.objects.filter(
    board_id=board.id,
    title='greeting',
  ).first()
  if not post:
    post = post_mo.POST(
      board_id=board.id,
      author_id='system',
      title='greeting',
      content='',
    )
    post.save()
  greeting_post = {
    'id': post.id,
  }

  # 가입 인사 작성 요청
  if request.method == 'POST':
    content = request.POST.get('content', '')
    if not content:
      return JsonResponse({'result': 'error'})

    # 이미 가입인사를 했는지 확인
    if post_mo.COMMENT.objects.filter(
      post_id=post.id,
      author_id=context['account']['id'],
    ).exists():
      return JsonResponse({'result': 'error'}) # 이미 가입인사를 한 경우, 에러 반환

    # 가입인사 포인트 확인
    point = int(core_mo.SERVER_SETTING.objects.get(id='comment_point').value)

    # 가입인사 댓글 작성
    comment = post_mo.COMMENT(
      post_id=post.id,
      author_id=context['account']['id'],
      content=content,
    )
    comment.save()

    # 사용자 활동 기록 추가 및 포인트 증가
    # 사용자 계정 및 파트너 계정만 해당
    if context['account']['account_type'] in ['user', 'dame', 'partner']:
      act = user_mo.ACTIVITY(
        user_id=context['account']['id'],
        location='/post/greeting',
        message=f'가입인사 댓글 작성',
        point_change=point,
      )
      act.save()

      # 사용자 계정일 경우, 포인트 증가
      account = get_user_model().objects.get(username=context['account']['id'])
      account.user_level_point += point
      account.user_usable_point += point
      account.save()

    return JsonResponse({'result': 'success'})

  # 가입인사 댓글 가져오기
  is_greeted = False
  page = int(request.GET.get('page', '1'))
  comments = post_do.get_post_comments(post.id)
  for comment in comments:
    if comment['author']['id'] == context['account']['id']:
      is_greeted = True
      break
  last_page = len(comments) // 50 + 1 # 한 페이지당 50개씩 표시
  comments = comments[50 * (page - 1):50 * page]

  return render(request, 'post/greeting.html', {
    **context,
    'comments': comments,
    'post': greeting_post,
    'last_page': last_page,
    'is_greeted': is_greeted,
  })

# 리뷰 게시판
# 리뷰 게시판에는, 주간, 월간, 데일리 베스트 리뷰 게시글 정보가 표시됨, 각 베스트 게시글은 10개씩 표시
# 리뷰 게시글은 이미지가 1개 이상 포함됨.
# 리뷰 게시글은 target_post가 존재.
# 리뷰 게시글의 순위를 나타내는 weight는 스케줄러에서 관리함.
def review(request):
  context = get_default_context(request)

  # board
  bo = post_mo.BOARD.objects.filter(post_type='review').first()
  if not bo:
    return redirect('/?redirect=not_found_board')
  board = {
    'id': bo.id,
    'name': bo.name,
  }

  # data
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')

  # search posts
  pos = post_mo.POST.objects.filter(
    board_id=bo.id,
    title__contains=search, # 검색. search가 비어있는 경우, 전체 글 검색
  ).order_by('-created_dt')
  last_page = len(pos) // 20 + 1 # 한 페이지당 20개씩 표시
  posts = post_do.get_reviews(pos[20 * (page - 1):20 * page])

  # best reviews
  # post.created_dt = models.DateTimeField(auto_now_add=True)
  if search == '' and page == 1: # 1 페이지의 검색이 없는 경우에만, best reviews를 가져옴

    # 오늘 날짜 문자열 확인
    today = datetime.datetime.now()

    # daily best reviews
    daily_reviews = []
    dps = post_mo.POST.objects.filter(
      Q(board_id=bo.id),
      Q(created_dt__year=today.year),
      Q(created_dt__month=today.month),
      Q(created_dt__day=today.day),
    ).order_by('-weight')[:10]
    daily_reviews = post_do.get_reviews(dps)


    # weekly best reviews
    weekly_reviews = []
    wps = post_mo.POST.objects.filter(
      Q(board_id=bo.id),
      Q(created_dt__year=today.year),
      Q(created_dt__week=today.isocalendar()[1]),
    ).order_by('-weight')[:10]
    weekly_reviews = post_do.get_reviews(wps)

    # monthly best reviews
    monthly_reviews = []
    mps = post_mo.POST.objects.filter(
      Q(board_id=bo.id),
      Q(created_dt__year=today.year),
      Q(created_dt__month=today.month),
    ).order_by('-weight')[:10]
    monthly_reviews = post_do.get_reviews(mps)

  else:
    daily_reviews = []
    weekly_reviews = []
    monthly_reviews = []

  return render(request, 'post/review.html', {
    **context,
    'board': board,
    'posts': posts,
    'last_page': last_page, # 마지막 페이지, page 처리에 사용
    'daily_reviews': daily_reviews,
    'weekly_reviews': weekly_reviews,
    'monthly_reviews': monthly_reviews,
  })

# 리뷰 게시글 작성
def write_review(request):
  context = get_default_context(request)
  # 사용자 계정만 리뷰 등록 가능
  if not (context['account']['account_type'] == 'dame' or context['account']['account_type'] == 'user'):
    return redirect('/?redirect=not_allowed')

  # board
  bo = post_mo.BOARD.objects.filter(post_type='review').first()
  board = {
    'id': bo.id,
    'name': bo.name,
  }

  # target post
  # 리뷰 대상 게시글이 있어야함.
  target_post_id = request.GET.get('post', '')
  tp = post_mo.POST.objects.filter(id=target_post_id).first()
  if not tp:
    return redirect('/?redirect=target_post_not_found')

  # 게시글 작성 처리
  if request.method == 'POST':
    title = request.POST.get('title', '')
    content = request.POST.get('content', '')
    images = request.POST.get('images', '')
    post = post_mo.POST(
      board_id=board.id,
      author_id=context['account']['id'],
      target_post_id=target_post_id,
      title=title,
      content=content,
      images=images,
    )
    post.save()

    # 사용자 활동 기록 추가
    # 사용자 계정만 해당
    if context['account']['account_type'] in ['user', 'dame']:
      point = core_mo.SERVER_SETTING.objects.get(id='post_point').value
      act = user_mo.ACTIVITY(
        user_id=context['account']['id'],
        location='/post/post_view?post=' + str(post.id),
        message=f'{board["name"]} 게시글 작성. ({title})',
        point_change=f'+{point}',
      )
      act.save()
      # 사용자 계정일 경우, 포인트 증가
      account = get_user_model().objects.get(username=context['account']['id'])
      account.user_level_point += point
      account.user_usable_point += point
      account.save()

    return JsonResponse({
      'result': 'success',
      'post_id': post.id,
    })

  # target post author
  tpa = get_user_model().objects.filter(
    username=tp.author_id,
    status='active',
  ).first()

  # target post data
  target_post = {
    'id': tp.id,
    'title': tp.title,
    'image': str(tp.images).split(',')[0],
    'author': {
      'id': tp.author_id,
      'nickname': tpa.first_name,
      'partner_categories': tpa.partner_categories,
      'partner_address': tpa.partner_address,
    },
    'created_dt': tp.created_dt,
    'view_count': len(str(tp.views).split(',')) - 1,
    'like_count': len(str(tp.bookmarks).split(',')) - 1,
    'comment_count': post_mo.COMMENT.objects.filter(post_id=tp.id).count(),
  }

  return render(request, 'post/write_review.html', {
    **context,
    'board': board,
    'post': target_post,
  })

# 리뷰 게시글 수정
def rewrite_review(request):
  context = get_default_context(request)

  # post
  post_id = request.GET.get('post', '')
  po = post_mo.POST.objects.filter(id=post_id).first()
  if not po: # 게시글이 없는 경우
    return redirect('/?redirect=post_not_found')
  if po.author_id != context['account']['id']: # 작성자가 아닌 경우
    # 관리자의 경우(게시글 권한이 있는) 게시글 수정 가능
    if context['account']['account_type'] == 'supervisor' or (context['account']['account_type'] == 'sub_supervisor' and 'post' in context['account']['supervisor_permissions']):
      pass
    else:
      return redirect('/?redirect=not_allowed')

  # board
  boards = []
  for bo in str(po.board_id).split(','):
    board = post_mo.BOARD.objects.filter(id=bo).first()
    if board:
      boards.append({
        'id': bo,
        'name': board.name,
      })

  # 게시글 수정 요청 처리
  if request.method == 'POST':
    title = request.POST.get('title', po.title)
    content = request.POST.get('content', po.content)
    images = request.POST.get('images', po.images)
    po.title = title
    po.content = content
    po.images = images
    po.save()

    # 사용자 활동 기록 추가
    # 사용자 계정만 해당
    if any(context['account']['account_type'] in s for s in ['user', 'dame']):
      act = user_mo.ACTIVITY(
        user_id=context['account']['id'],
        location='/post/post_view?post=' + post_id,
        message=f'[{boards[-1]["name"]}] 게시글 수정. ({title})',
        point_change='0',
      )
      act.save()

    return JsonResponse({
      'result': 'success',
      'post_id': po.id,
    })

  # target post
  tp = post_mo.POST.objects.filter(id=po.target_post_id).first()
  if not tp:
    return redirect('/?redirect=target_post_not_found')

  # target post author
  tpa = get_user_model().objects.filter(
    username=tp.author_id,
    status='active',
  ).first()

  # target post data
  target_post = {
    'id': tp.id,
    'title': tp.title,
    'images': str(tp.images).split(',')[0],
    'author': {
      'id': tp.author_id,
      'nickname': tpa.first_name,
      'partner_categories': tpa.partner_categories,
      'partner_address': tpa.partner_address,
    },
    'created_dt': tp.created_dt,
    'view_count': len(str(tp.views).split(',')) - 1,
    'bookmark_count': len(str(tp.bookmarks).split(',')) - 1,
    'comment_count': post_mo.COMMENT.objects.filter(post_id=tp.id).count(),
  }

  # post data
  post = {
    'id': po.id,
    'title': po.title,
    'boards': boards,
    'content': po.content,
    'images': str(po.images).split(','),
    'target_post': target_post,
  }

  return render(request, 'post/rewrite_review.html', {
    **context,
    'board': board,
    'post': post,
  })

# 리뷰 게시글 상세
def review_view(request):
  context = get_default_context(request)

  # post
  post_id = request.GET.get('post', '')
  po = post_mo.POST.objects.filter(id=post_id).first()
  if not po:
    return redirect('/?redirect=post_not_found')

  # board
  bos = str(po.board_id).split(',')
  boards = []
  for bo in bos:
    board = post_mo.BOARD.objects.filter(id=bo).first()
    if board:
      boards.append({
        'id': bo,
        'name': board.name,
      })

  # target post
  tp = post_mo.POST.objects.filter(id=po.target_post_id).first()
  if not tp:
    return redirect('/?redirect=target_post_not_found')

  # target post author
  tpa = get_user_model().objects.filter(
    username=tp.author_id,
    status='active',
  ).first()

  # target post data
  target_post = {
    'id': tp.id,
    'title': tp.title,
    'images': str(tp.images).split(','),
    'author': {
      'id': tp.author_id,
      'nickname': tpa.first_name,
      'partner_categories': tpa.partner_categories,
      'partner_address': tpa.partner_address,
    },
    'created_dt': tp.created_dt,
    'view_count': len(str(tp.views).split(',')) - 1,
    'bookmark_count': len(str(tp.bookmarks).split(',')) - 1,
    'comment_count': post_mo.COMMENT.objects.filter(post_id=tp.id).count(),
  }

  # post author
  pa = get_user_model().objects.filter(
    username=po.author_id,
    status='active',
  ).first()

  # post author level
  author_lv = core_mo.LEVEL_RULE.objects.get(level=pa.user_level)
  level = {
    'level': author_lv.level,
    'text_color': author_lv.text_color,
    'background_color': author_lv.background_color,
    'name': author_lv.name,
  }

  # author data
  author = {
    'id': po.author_id,
    'nickname': pa.first_name,
    'level': level,
    'account_type': pa.account_type,
  }

  # post data
  post = {
    'id': po.id,
    'title': po.title,
    'content': po.content,
    'images': str(po.images).split(','),
    'author': author,
    'boards': boards,
    'target_post': target_post,
    'created_dt': po.created_dt,
    'views': str(po.views).split(','),
    'bookmarks': str(po.bookmarks).split(','),
  }

  # comments
  comments = post_do.get_post_comments(post_id)

  # 조회수 증가
  if not context['account']['id'] in po.views:
    po.views += ',' + context['account']['id']
    po.save()
    post['views'].append(context['account']['id'])

  return render(request, 'post/review_view.html', {
    **context,
    'post': post,
    'comments': comments,
  })

# 여행 게시판
def travel(request):
  context = get_default_context(request)

  # board
  board_id = str(request.GET.get('board_ids', '')).split(',')[-1]
  bo = post_mo.BOARD.objects.filter(id=board_id).first()
  if bo.post_type != 'travel': # 여행 게시판이 아닌경우, 표준 게시판으로 이동
    return redirect('/post?board=' + board_id)
  board = {
    'id': bo.id,
    'name': bo.name,
    'display_permissions': bo.display_permissions,
    'enter_permissions': bo.enter_permissions,
    'write_permissions': bo.write_permissions,
    'comment_permissions': bo.comment_permissions,
  }
  # display_permissions 확인(게시판 접근 권한 확인)
  account_type = context['account']['account_type']
  if account_type == 'dame' and context['account']['status'] == 'pending':
    account_type = 'user' # dame 계정이 pending 상태인 경우, user로 처리
  if account_type not in board['display_permissions']:
    return redirect('/?redirect=not_allowed_board')

  # posts
  # 여행지 게시판은 page, search 말도고 category 검색 조건이 추가로 있음.
  # category는 게시글 작성자 데이터베이스 필드에 있으므로, 게시글 filter 후, author를 확인하여 검색
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')
  category = request.GET.get('category', '')

  # search
  posts = []
  pos = post_mo.POST.objects.filter(
    Q(board_id__contains=board_id) & Q(title__contains=search),
  ).order_by('-created_dt')
  # 카테고리 검색을 위한 파트너 데이터베이스 필드 확인
  category_partners = [ partner.username for partner in get_user_model().objects.filter(partner_categories__contains=category)]
  for po in pos:
    if po.author_id in category_partners: # 카테고리 검색 조건 추가

      # post author
      pa = get_user_model().objects.filter(
        username=po.author_id,
        status='active',
      ).first()

      # author data
      author = {
        'id': po.author_id,
        'nickname': pa.first_name,
        'partner_categories': pa.partner_categories,
        'partner_address': pa.partner_address,
        'account_type': pa.account_type,
      }

      # post data
      posts.append({
        'id': po.id,
        'title': po.title,
        'author': author,
        'image': str(po.images).split(',')[0],
        'created_dt': po.created_dt,
        'view_count': len(str(po.views).split(',')) - 1,
        'bookmark_count': len(str(po.bookmarks).split(',')) - 1,
        'comment_count': post_mo.COMMENT.objects.filter(post_id=po.id).count(),
      })
  last_page = len(posts) // 20 + 1 # 한 페이지당 20개씩 표시
  posts = posts[20 * (page - 1):20 * page]

  # categories
  categories = partner_do.get_categories()

  return render(request, 'post/travel.html', {
    **context,
    'board': board,
    'posts': posts,
    'last_page': last_page,
    'categories': categories,
  })

# 여행 게시글 상세보기
def travel_view(request):
  context = get_default_context(request)

  # data
  post_id = request.GET.get('post', '')

  # post
  po = post_mo.POST.objects.filter(id=post_id).first()
  if not po:
    return redirect('/')

  # board
  bos = str(po.board_id).split(',')
  post_boards = []
  for bo in bos:
    if bo != '':
      post_boards.append({
        'id': bo,
        'name': post_mo.BOARD.objects.get(id=bo).name,
      })

  # post author
  pa = get_user_model().objects.filter(
    username=po.author_id,
    status='active',
  ).first()

  # author data
  author = {
    'id': po.author_id,
    'nickname': pa.first_name,
    'partner_categories': pa.partner_categories,
    'partner_address': pa.partner_address,
    'account_type': pa.account_type,
  }

  # post data
  post = {
    'id': str(po.id),
    'title': po.title,
    'content': po.content,
    'images': str(po.images).split(','),
    'author': author,
    'boards': post_boards,
    'created_dt': po.created_dt,
    'views': str(po.views).split(','),
    'bookmarks': str(po.bookmarks).split(','),
  }

  # comments
  comments = post_do.get_post_comments(post_id)

  # categories
  categories = partner_do.get_categories()

  # add views
  if not context['account']['id'] in po.views:
    po.views += ',' + context['account']['id']
    po.save()
    post['views'].append(context['account']['id'])

  return render(request, 'post/travel_view.html', {
    **context,
    'post': post,
    'comments': comments,
    'categories': categories,
  })


