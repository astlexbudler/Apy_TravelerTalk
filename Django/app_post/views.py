import datetime
import random
import string
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, logout, get_user_model
from django.db.models import Q

from app_core import models
from app_core import daos

# 게시판 페이지
# 이 페이지는 아래와 같은 경우로 나뉨
# 1. 특정 게시판으로 이동을 요청하는 경우 => 해당 게시판으로 redirect
# 2. 전체 글 검색을 하는 경우(board_id 가 없음) => 전체 게시글 검색
# 3. 사전 정의되지 않은 기타 게시판의 경우 => 해당 게시글 검색
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
  boards = daos.get_board_tree(account_type) # 게시판 정보

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids') # 게시판 아이디
  page = int(request.GET.get('page', '1')) # 페이지
  search = request.GET.get('search', '') # 검색어

  # board_ids 확인
  if not board_ids: # 게시판 아이디가 없는 경우
    return redirect('/?redirect_message=not_found_board') # 게시판이 없는 경우, 메인 페이지로 이동
  board_ids = board_ids.split(',') # 게시판 아이디를 리스트로 변환

  # 게시판 접근 권한 확인
  selected_boards = daos.get_selected_board_info(board_ids) # 선택된 게시판 정보
  writable = False
  for board in selected_boards:
    if account_type not in board['enter']: # enter 권한 확인
      return redirect('/?redirect_message=not_allowed_board') # 권한이 없는 경우, 메인 페이지로 이동
    if account_type in board['write']: # write 권한 확인
      writable = True

  # 게시판이 사전 정의된 게시판인지 확인
  board = models.BOARD.objects.filter(id=board_ids[-1]).first() # 게시판 정보 가져오기(마지막 게시판 정보)
  if not board: # 게시판이 존재하지 않는 경우
    return redirect('/?redirect_message=not_found_board')
  if board.board_type == 'attendance': # 출석체크 게시판인 경우
    return redirect('/post/attendance')
  elif board.board_type == 'greeting': # 가입인사 게시판인 경우
    return redirect('/post/greeting')
  elif board.board_type == 'review':
    return redirect('/post/review')
  elif board.board_type == 'travel':
    return redirect('/post/travel')

  # 게시글 가져오기
  posts, last_page = daos.get_board_posts(board_ids, page, search)

  return render(request, 'post/index.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 게시판 정보
    'writable': writable, # 게시글 작성 가능 여부
    'posts': posts, # 게시글 정보
    'last_page': last_page, # 마지막 페이지, page 처리에 사용
  })

# 게시글 작성 페이지
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
  boards = daos.get_board_tree(account_type) # 게시판 정보
  if not request.user.is_authenticated: # 로그인 되지 않은 경우
    return redirect('/?redirect_message=need_login') # 로그인 필요 메세지 표시

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids')

  # board_ids가 없는 경우, 메인 페이지로 이동
  if not board_ids:
    return redirect('/?redirect_message=not_found_board')
  board_ids = board_ids.split(',') # 게시판 아이디를 리스트로 변환

  # 게시판 접근 권한 확인
  selected_boards = daos.get_selected_board_info(board_ids) # 선택된 게시판 정보
  for board in selected_boards:
    if account_type not in board['write']: # write 권한 확인
      return redirect('/?redirect_message=not_allowed_board')

  # 게시판이 사전 정의된 게시판인지 확인
  board = models.BOARD.objects.filter(id=board_ids[-1]).first() # 게시판 정보 가져오기(마지막 게시판 정보)
  if not board: # 게시판이 존재하지 않는 경우
    return redirect('/?redirect_message=not_found_board')
  if board.board_type == 'attendance': # 출석체크 게시판인 경우
    return redirect('/post/attendance')
  elif board.board_type == 'greeting': # 가입인사 게시판인 경우
    return redirect('/post/greeting')


  # 게시글 작성 처리 요청
  if request.method == 'POST':
    title = request.POST.get('title')
    content = request.POST.get('content')
    image_paths = request.POST.get('image_paths') # 이벤트나 리뷰 게시글 작성 시 이미지 경로
    review_post_id = request.POST.get('review_post_id') # 리뷰 게시글 작성시, 대상 게시글 아이디
    board_ids = request.GET.get('board_ids') # 게시판 아이디
    if not title or not content: # 제목 또는 내용이 없는 경우
      return JsonResponse({'result': 'error'})
    board_ids = [int(b) for b in board_ids.split(',')]
    boards = models.BOARD.objects.filter(id__in=board_ids)
    if not boards:
      return JsonResponse({'result': 'error'})

    post = models.POST.objects.create(
      author=request.user,
      title=title,
      content=content,
      image_paths=image_paths,
    )
    post.boards.add(*boards)
    if review_post_id:
      review_post = models.POST.objects.filter(id=review_post_id).first()
      if review_post:
        post.review_post = review_post
    post.save()

    # 사용자 활동 기록 추가
    # 사용자 계정 및 파트너 계정만 해당
    models.ACTIVITY.objects.create(
      account=request.user,
      message = f'[게시글] {title} 게시글을 작성하였습니다.',
    )
    if account_type in ['user', 'dame']:
      point = int(models.SERVER_SETTING.objects.get(name='post_point').value)
      request.user.level_point += point
      request.user.coupon_point += point
      request.user.save()

    return JsonResponse({'result': 'success', 'post_id': post.id})

  return render(request, 'post/write_post.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 게시판 정보
  })

# 게시글 수정 페이지
def rewrite_post(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  post_id = request.GET.get('post')

  # post 확인
  post = daos.get_post_info(post_id)
  if not post:
    return redirect('/?redirect_message=not_found_post')

  # 게시물 수정 권한 확인(작성자 또는 관리자 또는 게시글 권한이 있는 부관리자가 가능)
  if (contexts['account']['id'] != post['author']['id']) or ('supervisor' not in contexts['account']['groups']) or not (('post' in contexts['account']['subsupervisor_permissions']) and 'subsupervisor' in contexts['account']['groups']):
    return redirect('/?redirect_message=not_allowed')

  '''
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
  '''

  return render(request, 'post/rewrite_post.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'post': post, # 게시글 정보
  })

# 게시글 상세 페이지
def post_view(request):
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
  boards = daos.get_board_tree(account_type) # 게시판 정보

  # 데이터 가져오기
  post_id = request.GET.get('post_id')

  # post 확인
  post = daos.get_post_info(post_id)

  board_ids = [
    board.id for board in models.BOARD.objects.filter(name__in=post['boards'])
  ]
  selected_boards = daos.get_selected_board_info(board_ids) # 선택된 게시판 정보
  commentable = False
  for board in selected_boards:
    if account_type not in board['enter']: # enter 권한 확인
      return redirect('/?redirect_message=not_allowed_board') # 권한이 없는 경우, 메인 페이지로 이동
    if account_type in board['comment']: # write 권한 확인
      commentable = True

  # 댓글 가져오기
  comments = daos.get_all_post_comments(post_id)

  # 조회수 증가
  if post_id not in  request.session.get('view_posts', ''):
    request.session['view_posts'] = request.session.get('view_posts', '') + ',' + post_id
    po = models.POST.objects.get(id=post_id)
    po.view_count += 1
    po.save()

  return render(request, 'post/post_view.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'post': post, # 게시글 정보
    'commentable': commentable, # 댓글 작성 가능 여부
    'comments': comments, # 댓글 정보
  })

# 출석체크 게시판
def attendance(request):
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
  boards = daos.get_board_tree(account_type) # 게시판 정보

  # 권한 확인
  if not request.user.is_authenticated:
    # 게스트는 출석체크 게시판 접근 불가
    return redirect('/?redirect_message=need_login')

  # 출석체크 게시판
  b = models.BOARD.objects.filter(board_type='attendance').first()
  board = {
    'id': b.id,
    'name': b.name,
  }

  # 출석 체크 게시플 가져오기
  # 춣석체크는 오늘 날짜의 출석체크 게시글에 댓글을 다는걸로 구현됨.
  today = datetime.datetime.now().strftime('%Y-%m-%d')
  post = models.POST.objects.filter(
    title=f'attendance:{today}',
  ).first()
  if not post: # 만약 오늘의 출석체크 게시긇이 없다면, 생성
    post = models.POST.objects.create(
      title=f'attendance:{today}',
      content='',
    )
    post.boards.add(b)
    post.save()

  # 댓글 가져오기
  comments = daos.get_all_post_comments(post.id)

  '''
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
  '''

  # 사용자가 이전에 출석한 날짜 가져오기
  is_attended = False
  attend_days = []
  monthPosts = models.POST.objects.filter(
    title__contains=f'attendance:{datetime.datetime.now().strftime("%Y-%m")}', # 이번달 출석체크 게시글
  )
  for post in monthPosts:
    attend = models.COMMENT.objects.filter(
      post = post,
      author=request.user,
    ).first()
    if attend: # 출석 댓글이 있는 경우,
      attend_days.append(int(post.title.split('-')[-1])) # 출석 체크한 날짜 추가
      if today in post.title: # 오늘 출석체크를 했는지 확인
        is_attended = True

  return render(request, 'post/attendance.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'comments': comments, # 출석 체크 글
    'post': post, # 출석체크 게시글
    'board': board, # 출석체크 게시판
    'attend_days': attend_days, # 이번달에 출석체크한 날짜
    'is_attended': is_attended, # 오늘 출석체크를 했는지 여부
  })

# 가입인사 게시판
def greeting(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree() # 게시판 정보 가져오기

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=need_login') # 게스트는 가입인사 게시판 접근 불가

  # 가입인사 게시판
  b = models.BOARD.objects.filter(post_type='greeting').first()
  board = {
    'id': b.id,
    'name': b.name,
  }

  # 가입인사 게시글 가져오기
  post = models.POST.objects.filter(
    board_id=b.id,
    title='greeting',
  ).first()
  if not post:
    post = models.POST(
      board_id=b.id,
      title='greeting',
    )
    post.save()

  # 가입 인사 작성 요청
  '''
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
  '''

  # 가입인사 댓글 가져오기
  is_greeted = False
  comments = daos.get_all_post_comments(post.id)
  for comment in comments:
    if comment['author']['id'] == contexts['account']['id']:
      is_greeted = True
      break

  return render(request, 'post/greeting.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'comments': comments, # 가입인사 댓글
    'post': post, # 가입인사 게시글
    'is_greeted': is_greeted, # 가입인사를 했는지 여부
  })

# 리뷰 게시판
# 리뷰 게시판에는, 주간, 월간, 데일리 베스트 리뷰 게시글 정보가 표시됨, 각 베스트 게시글은 10개씩 표시
# 리뷰 게시글은 이미지가 1개 이상 포함됨.
# 리뷰 게시글은 target_post가 존재.
# 리뷰 게시글의 순위를 나타내는 weight는 스케줄러에서 관리함.
def review(request):
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
  boards = daos.get_board_tree(account_type) # 게시판 정보

  # 리뷰 게시판
  b = models.BOARD.objects.filter(post_type='review').first()
  board = {
    'id': b.id,
    'name': b.name,
  }

  # 데이터 가져오기
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')

  # search posts
  posts, last_page = daos.get_board_posts(b.id, page, search)

  if page == 1 and search == '':
    # best reviews
    # 오늘의 베스트 리뷰(추천, 조회, 업로드 순)
    today = timezone.localtime().date()
    today_best_reviews = []
    tbrs = models.POST.objects.select_related('author', 'review_post').filter(
      board_id=b.id,
      created_at__date=today,
    ).order_by('-like_count', '-view_count', '-created_at')[:10]
    for tbr in tbrs:
      today_best_reviews.append({
        'id': tbr.id,
        'title': tbr.title,
        'image_paths': str(tbr.image_paths).split(','), # 이미지 경로
        'author': {
          'nickname': tbr.author.first_name,
        },
        'review_post': {
          'title': tbr.review_post.title,
        },
        'like_count': tbr.like_count,
        'view_count': tbr.view_count,
        'created_at': tbr.created_at,
      })
    # 주간 베스트 리뷰(weight 기준)
    weekly_best_reviews = []
    wbrs = models.POST.objects.select_related('author', 'review_post').filter(
      board_id=b.id,
      created_at__gte=today - datetime.timedelta(days=7),
    ).order_by('-weight')[:10]
    for wbr in wbrs:
      weekly_best_reviews.append({
        'id': wbr.id,
        'title': wbr.title,
        'image_paths': str(wbr.image_paths).split(','), # 이미지 경로
        'author': {
          'nickname': wbr.author.first_name,
        },
        'review_post': {
          'title': wbr.review_post.title,
        },
        'like_count': wbr.like_count,
        'view_count': wbr.view_count,
        'created_at': wbr.created_at,
      })
    # 월간 베스트 리뷰(weight 기준)
    now = timezone.localtime()
    monthly_best_reviews = []
    mbrs = models.POST.objects.select_related('author', 'review_post').filter(
      board_id=b.id,
      created_at__year=now.year,
      created_at__month=now.month,
    ).order_by('-weight')[:10]
    for mbr in mbrs:
      monthly_best_reviews.append({
        'id': mbr.id,
        'title': mbr.title,
        'image_paths': str(mbr.image_paths).split(','), # 이미지 경로
        'author': {
          'nickname': mbr.author.first_name,
        },
        'review_post': {
          'title': mbr.review_post.title,
        },
        'like_count': mbr.like_count,
        'view_count': mbr.view_count,
        'created_at': mbr.created_at,
      })

  return render(request, 'post/review.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 리뷰 게시판
    'posts': posts, # 리뷰 게시글
    'last_page': last_page, # 마지막 페이지, page 처리에 사용
    'today_reviews': today_best_reviews, # 오늘의 베스트 리뷰
    'weekly_reviews': weekly_best_reviews, # 주간 베스트 리뷰
    'monthly_reviews': monthly_best_reviews, # 월간 베스트 리뷰
  })

# 리뷰 게시글 작성
def write_review(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree() # 게시판 정보 가져오기

  # 사용자 계정만 리뷰 등록 가능
  if not request.user.is_authenticated:
    return redirect('/?redirect=need_login') # 로그인 필요
  if 'partner' in contexts['account']['groups'] or 'supervisor' in contexts['account']['groups'] or 'subsupervisor' in contexts['account']['groups']:
    return redirect('/?redirect=not_allowed') # 파트너, 관리자는 리뷰 작성 불가

  # 리뷰 게시판
  b = models.BOARD.objects.filter(post_type='review').first()
  board = {
    'id': b.id,
    'name': b.name,
  }

  # 데이터
  review_post_id = request.GET.get('post_id')

  # 리뷰 대상 게시글 확인
  if not review_post_id: # 리뷰 대상 게시글이 없는 경우
    return redirect('/?redirect=target_post_not_found') # 리뷰 대상 게시글이 없는 경우
  review_post = daos.get_post_info(review_post_id)

  # 게시글 작성 처리
  '''
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
  '''

  return render(request, 'post/write_review.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 리뷰 게시판
    'review_post': review_post, # 리뷰 대상 게시글
  })

# 리뷰 게시글 수정
def rewrite_review(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree() # 게시판 정보 가져오기

  # 로그인 여부 확인
  if not request.user.is_authenticated: # 로그인이 되어 있지 않은 경우
    return redirect('/?redirect_message=need_login') # 로그인 페이지로 리다이렉트

  # 데이터 가져오기
  post_id = request.GET.get('post_id')

  # 리뷰 게시판
  b = models.BOARD.objects.filter(post_type='review').first()
  board = {
    'id': b.id,
    'name': b.name,
  }

  # 리뷰 게시글 확인
  post = daos.get_post_info(post_id)
  if not post: # 게시글이 없는 경우
    return redirect('/?redirect_message=not_found_post')
  # 게시물 수정 권한 확인(작성자 또는 관리자 또는 게시글 권한이 있는 부관리자가 가능)
  if (contexts['account']['id'] != post['author']['id']) or ('supervisor' not in contexts['account']['groups']) or not (('post' in contexts['account']['subsupervisor_permissions']) and 'subsupervisor' in contexts['account']['groups']):
    return redirect('/?redirect_message=not_allowed')

  # 리뷰 대상 게시글 확인
  review_post = daos.get_post_info(post['review_post']['id'])

  # 게시글 수정 요청 처리
  '''
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
  '''

  return render(request, 'post/rewrite_review.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 리뷰 게시판
    'post': post, # 리뷰 게시글
    'review_post': review_post, # 리뷰 대상 게시글
  })

# 리뷰 게시글 상세
def review_view(request):
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
  boards = daos.get_board_tree(account_type) # 게시판 정보

  # 데이터 가져오기
  post_id = request.GET.get('post_id')

  # 게시글 확인
  post = daos.get_post_info(post_id)
  if not post:  # 게시글이 없는 경우
    return redirect('/?redirect=post_not_found') # 메인 페이지로 이동

  # 게시판 정보
  b = models.BOARD.objects.filter(id=post['boards'][0]).first()
  board = {
    'id': b.id,
    'name': b.name,
  }

  # 댓글 가져오기
  comments = daos.get_all_post_comments(post_id)

  # 조회수 증가
  if post_id not in request.session.get('view_posts', ''):
    request.session['view_posts'] = request.session.get('view_posts', '') + ',' + post_id
    po = models.POST.objects.get(id=post_id)
    po.view_count += 1
    po.save()

  return render(request, 'post/review_view.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'post': post, # 게시글 정보
    'board': board, # 게시판 정보
    'comments': comments, # 댓글 정보
  })

# 여행 게시판
def travel(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids')
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')
  categories = request.GET.get('categories', '')

  # 여행 게시판
  selected_boards = daos.get_selected_board_info(board_ids)

  # 게시글 가져오기
  posts = []
  ps = models.POST.objects.select_related('author', 'place_info').prefetch_related('place_info__categories').exclude(
    review_post__isnull=True
  ).filter(
    title__contains=search, # 검색어가 제목에 포함된 경우
    place_info__categories=categories, # 카테고리 검색 조건 추가
  ).order_by('search_weight')
  last_page = (ps.count() // 20) + 1
  ps = ps[(page - 1) * 20:page * 20] # 각 페이지에 20개씩 표시
  for p in ps:
    posts.append({
      'id': p.id,
      'title': p.title,
      'author': {
        'nickname': p.author.first_name,
      },
      'place_info': {
        'categories': [c.name for c in p.place_info.categories],
        'address': p.place_info.address,
        'location_info': p.place_info.location_info,
        'open_info': p.place_info.open_info,
        'status': 'ad',
      },
      'view_count': p.view_count,
      'like_count': p.like_count,
      'created_at': p.created_at,
    })

  # 카테고리 정보 가져오기
  categories = daos.get_category_tree()

  return render(request, 'post/travel.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'selected_boards': selected_boards, # 게시판 정보
    'posts': posts, # 게시글 정보
    'last_page': last_page, # 마지막 페이지
    'categories': categories, # 카테고리 정보
  })

# 여행 게시글 상세보기
def travel_view(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  post_id = request.GET.get('post_id', '')

  # 게시글 확인
  post = daos.get_post_info(post_id)
  if not post: # 게시글이 없는 경우
    return redirect('/?redirect=post_not_found') # 메인 페이지로 이동

  # 게시판 정보
  comments = daos.get_all_post_comments(post_id)

  # 조회수 증가
  if post_id not in request.session.get('view_posts', ''):
    request.session['view_posts'] = request.session.get('view_posts', '') + ',' + post_id
    po = models.POST.objects.get(id=post_id)
    po.view_count += 1
    po.save()

  return render(request, 'post/travel_view.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'post': post, # 게시글 정보
    'comments': comments, # 댓글 정보
  })

# 익명 게시판 페이지
def anominous(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids')
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')

  # 익명 게시판
  selected_boards = daos.get_selected_board_info(board_ids)

  # 게시글 가져오기
  posts, last_page = daos.get_board_posts(board_ids, page, search)
  for post in posts:
    post['author']['nickname'] = ''

  return render(request, 'post/anominous.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'selected_boards': selected_boards, # 선택된 게시판 정보
    'posts': posts, # 게시글 정보
    'last_page': last_page, # 마지막 페이지, page 처리에 사용
  })

# 익명 게시글 상세보기
def anominous_view(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  post_id = request.GET.get('post_id', '')

  # 게시글 확인
  post = daos.get_post_info(post_id)
  if not post: # 게시글이 없는 경우
    return redirect('/?redirect=post_not_found') # 메인 페이지로 이동
  post['author']['nickname'] = ''

  # 게시판 정보
  comments = daos.get_all_post_comments(post_id)
  for comment in comments:
    comment['author']['nickname'] = ''

  # 조회수 증가
  if post_id not in request.session.get('view_posts', ''):
    request.session['view_posts'] = request.session.get('view_posts', '') + ',' + post_id
    po = models.POST.objects.get(id=post_id)
    po.view_count += 1
    po.save()

  return render(request, 'post/anominous_view.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'post': post, # 게시글 정보
    'comments': comments, # 댓글 정보
  })
