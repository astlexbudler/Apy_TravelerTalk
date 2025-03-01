import datetime
import random
import string
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, logout, get_user_model
from django.db.models import Q
from django.db.models import Case, When, IntegerField

from app_core import models
from app_core import daos

# 게시판 페이지
# 이 페이지는 아래와 같은 경우로 나뉨
# 1. 특정 게시판으로 이동을 요청하는 경우 => 해당 게시판으로 redirect
# 2. 전체 글 검색을 하는 경우(board_id 가 없음) => 전체 게시글 검색
# 3. 사전 정의되지 않은 기타 게시판의 경우 => 해당 게시글 검색
def index(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree(contexts['account']['account_type']) # 게시판 정보

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids') # 게시판 아이디
  page = int(request.GET.get('page', '1')) # 페이지
  search = request.GET.get('search', '') # 검색어

  # board_ids 확인
  if not board_ids: # 게시판 아이디가 없는 경우
    return redirect('/?redirect_message=not_found_board') # 게시판이 없는 경우, 메인 페이지로 이동
  board_ids = board_ids.split(',') # 게시판 아이디를 리스트로 변환
  board = daos.select_board(board_ids[-1]) # 마지막 게시판 정보 가져오기

  # 게시판 접근 권한 확인
  writable = False
  if contexts['account']['account_type'] not in board['enter_groups']: # enter 권한 확인
    return redirect('/?redirect_message=not_allowed_board') # 권한이 없는 경우, 메인 페이지로 이동
  if contexts['account']['account_type'] in board['write_groups']:
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
    return redirect('/post/review?board_ids=' + request.GET.get('board_ids') + '&page=' + str(page) + '&search=' + search)
  elif board.board_type == 'travel':
    return redirect('/post/travel?board_ids=' + request.GET.get('board_ids') + '&page=' + str(page) + '&search=' + search)
  # 레벨 제한 확인
  if contexts['account']['account_type'] in ['user', 'dame', 'guest']:
    if board.level_cut > int(contexts['account']['level']['level']):
      return redirect('/?redirect_message=not_allowed_board')

  # 게시글 가져오기
  posts, last_page = daos.search_posts(
    title=search,
    board_id=board_ids[-1],
    page=page,
  )

  return render(request, 'post/board.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 게시판 정보
    'writable': writable, # 게시글 작성 가능 여부
    'posts': posts, # 게시글 정보
    'last_page': last_page, # 마지막 페이지
  })

# 게시글 작성 페이지
def write_post(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree(contexts['account']['account_type']) # 게시판 정보

  # 게시글 작성 처리 요청
  if request.method == 'POST':
    title = request.POST.get('title')
    content = str(request.POST.get('content')).replace('`', "'")
    review_post_id = request.POST.get('review_post_id') # 후기 게시글 작성시, 대상 게시글 아이디
    image = request.FILES.get('image') if request.FILES.get('image') else None
    review_post_id = request.POST.get('review_post_id') # 후기 게시글 작성시, 대상 게시글 아이디
    board_ids = request.GET.get('board_ids') # 게시판 아이디
    if not title or not content: # 제목 또는 내용이 없는 경우
      return JsonResponse({'result': 'error'})

    # 리뷰 게시글인 경우
    if review_post_id:
      board = daos.select_board(
        models.BOARD.objects.filter(board_type='review').id
      )
      board_ids = board['ids']

    # 게시글 작성
    print('board_ids:', board_ids)
    post = daos.create_post(
      author_id=request.user.id,
      title=title,
      content=content,
      board_ids=board_ids,
      related_post_id=review_post_id,
      image=image,
    )

    # 사용자 활동 기록 추가 및 포인트
    # 사용자 계정 및 파트너 계정만 해당
    if review_post_id:
      point = int(models.SERVER_SETTING.objects.get(name='review_point').value)
      daos.create_account_activity(
        account_id=request.user.id,
        message=f'[후기] {title} 후기를 작성하였습니다.',
        exp_change=point,
        mileage_change=point,
      )
      daos.update_account(
        account_id=request.user.id,
        exp_change=point,
        mileage_change=point,
      )
    else:
      point = int(models.SERVER_SETTING.objects.get(name='post_point').value)
      daos.create_account_activity(
        account_id=request.user.id,
        message=f'[게시글] {title} 게시글을 작성하였습니다.',
        exp_change=point,
        mileage_change=point,
      )
      daos.update_account(
        account_id=request.user.id,
        exp=request.user.exp + point,
        mileage=request.user.mileage + point,
      )

    return JsonResponse({'result': 'success', 'post_id': post['pk']})

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids')
  review_post_id = request.GET.get('review_post_id')

  # board_ids가 없는 경우, 메인 페이지로 이동
  if not board_ids and not review_post_id:
    return redirect('/?redirect_message=not_found_board')
  board_ids = str(board_ids).split(',') # 게시판 아이디를 리스트로 변환
  board = daos.select_board(board_ids[-1]) # 마지막 게시판 정보 가져오기

  # 게시판 접근 권한 확인
  if review_post_id: # 후기 게시글 작성인 경우
    if contexts['account']['account_type'] not in ['user', 'dame']: # 사용자, 파트너 계정만 가능
      return redirect('/?redirect_message=not_allowed_board')
    board = daos.select_board(models.BOARD.objects.filter(board_type='review').first().id) # 마지막 게시판 정보 가져오기
  else:
    if contexts['account']['account_type'] not in board['write_groups']: # write 권한 확인
      return redirect('/?redirect_message=not_allowed_board')

  # 게시판이 사전 정의된 게시판인지 확인
  if not board: # 게시판이 존재하지 않는 경우
    return redirect('/?redirect_message=not_found_board')
  if board['board_type'] == 'attendance': # 출석체크 게시판인 경우
    return redirect('/post/attendance')
  elif board['board_type'] == 'greeting': # 가입인사 게시판인 경우
    return redirect('/post/greeting')
  # 레벨 제한 확인
  if contexts['account']['account_type'] in ['user', 'dame']:
    if board['level_cut'] > int(contexts['account']['level']['level']):
      return redirect('/?redirect_message=not_allowed_board')

  # 후기 게시글인 경우
  if review_post_id:
    review_post = daos.select_post(review_post_id)
  else:
    review_post = None

  return render(request, 'post/write_post.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 게시판 정보
    'review_post': review_post, # 후기 게시글 정보
  })

# 게시글 수정 페이지
def rewrite_post(request):
  # account, activities(5), unread_messages(5), coupons(5), server, best_reviews(5)
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree(contexts['account']['account_type']) # 게시판 정보

  # 데이터 가져오기
  post_id = request.GET.get('post_id')

  # post 확인
  post = daos.get_post_info(post_id)
  if not post:
    return redirect('/?redirect_message=not_found_post')

  # 게시물 수정 권한 확인(작성자 또는 관리자 또는 게시글 권한이 있는 부관리자가 가능)
  if post['author']['id'] != contexts['account']['id']:
    if contexts['account']['account_type'] == 'supervisor' or (contexts['account']['account_type'] == 'subsupervisor' and 'post' in contexts['account']['subsupervisor_permissions']):
      pass
    else:
      return redirect('/?redirect_message=not_allowed')

  # 게시판 확인
  last_board_name = post['boards'][-1]
  board = models.BOARD.objects.filter(name=last_board_name).first()

  # 게시글 수정 요청
  if request.method == 'POST':
    title = request.POST.get('title')
    content = str(request.POST.get('content')).replace('`', "'")
    image = request.FILES.get('image') if request.FILES.get('image') else None
    if not title or not content: # 제목 또는 내용이 없는 경우
      return JsonResponse({'result': 'error'})
    if not boards:
      return JsonResponse({'result': 'error'})

    # 게시글 수정
    post = models.POST.objects.get(id=post_id)
    post.title = title
    post.content = content
    if image:
      post.image = image
    post.save()

    # 사용자 활동 기록 추가
    models.ACTIVITY.objects.create(
      account=request.user,
      message = f'[게시글] {title} 게시글을 수정하였습니다.',
    )

    return JsonResponse({'result': 'success', 'post_id': post.id})

  return render(request, 'post/rewrite_post.html', {
    **contexts, # 기본 컨텍스트 정보
    'boards': boards, # 게시판 정보
    'board': board, # 게시판 정보
    'post': post, # 게시글 정보
  })

# 게시글 상세 페이지
def post_view(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree(contexts['account']['account_type']) # 게시판 정보

  # 데이터 가져오기
  post_id = request.GET.get('post_id')

  # 삭제 요청 처리
  if request.method == 'DELETE':
    post = models.POST.objects.select_related('author').filter(
      id=post_id
    ).first()

    # 게시글 작성자 확인
    if request.user.username != post.author.id:
      # 관리자 또는 부관리자(게시글 권한이 있는) 확인
      if contexts['account']['account_type'] == 'supervisor' or (contexts['account']['account_type'] == 'subsupervisor' and 'post' in contexts['account']['subsupervisor_permissions']):
        pass
      else:
        return JsonResponse({'result': 'error'})

    # 게시글 삭제
    if post:
      # 사용자 활동 기록 추가
      if request.user.username != post.author.id:
        models.ACTIVITY.objects.create(
          account=request.user,
          message = f'[게시글] {post.title} 게시글을 삭제하였습니다.',
        )
      else:
        models.ACTIVITY.objects.create(
          account=post.author,
          message = f'[게시글] {post.title} 게시글이 관리자에 의해 삭제되었습니다.',
        )
      post.delete()

    return JsonResponse({'result': 'success'})

  # post 확인
  post = daos.select_post(post_id)

  # 여행지 게시글인지 확인
  if post['place_info']:
    return redirect('/post/travel_view?post_id=' + post_id)

  # 댓글 권한 확인
  commentable = False
  if contexts['account']['account_type'] in post['boards'][-1]['comment_groups']:
    commentable = True

  # 레벨 제한 확인
  if contexts['account']['account_type'] in ['user', 'dame']:
    if post['boards'][-1]['level_cut'] > int(contexts['account']['level']['level']):
      return redirect('/?redirect_message=not_allowed_board')

  # 댓글 가져오기
  comments = daos.select_comments(post_id)

  # 조회수 증가
  if post_id not in  request.session.get('view_posts', ''):
    request.session['view_posts'] = request.session.get('view_posts', '') + ',' + post_id
    daos.update_post(
      post_id=post_id,
      view_count=int(post['view_count']) + 1,
    )

  return render(request, 'post/post_view.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'post': post, # 게시글 정보
    'board': post['boards'][-1], # 게시판 정보
    'commentable': commentable, # 댓글 작성 가능 여부
    'comments': comments, # 댓글 정보
  })

# 출석체크 게시판
def attendance(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree(contexts['account']['account_type']) # 게시판 정보

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
  comments = daos.select_comments(post.id)

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

  # 출석 포인트
  attend_point = {
    'first': int(daos.select_server_setting('attend_point')),
    'second': int(daos.select_server_setting('attend_point')) * 1.5,
    'third': int(daos.select_server_setting('attend_point')) * 1.2
  }

  return render(request, 'post/attendance.html', {
    **contexts, # 기본 컨텍스트 정보
    'boards': boards, # 게시판 정보
    'comments': comments, # 출석 체크 글
    'post': post, # 출석체크 게시글
    'board': board, # 출석체크 게시판
    'attend_days': attend_days, # 이번달에 출석체크한 날짜
    'commentable': not is_attended, # 오늘 출석체크를 했는지 여부
    'attend_point': attend_point, # 출석체크 포인트
  })

# 가입인사 게시판
def greeting(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree(contexts['account']['account_type']) # 게시판 정보

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=need_login') # 게스트는 가입인사 게시판 접근 불가

  # 데이터 가져오기
  page = int(request.GET.get('page', '1'))

  # 가입인사 게시판
  b = models.BOARD.objects.filter(board_type='greeting').first()
  board = {
    'id': b.id,
    'name': b.name,
  }

  # 가입인사 게시글 가져오기
  post = models.POST.objects.filter(
    boards__id__in=[str(b.id)],
    title='greeting',
  ).first()
  if not post:
    post = models.POST.objects.create(
      title='greeting',
    )
    post.boards.add(b)
    post.save()

  # 가입인사 댓글 가져오기
  is_greeted = False
  comments = daos.select_comments(post.id)
  for comment in comments:
    if comment['author']['id'] == contexts['account']['id']:
      is_greeted = True
      break
  last_page = len(comments) // 20 + 1
  comments = comments[(page - 1) * 20:page * 20]

  return render(request, 'post/greeting.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 가입인사 게시판
    'last_page': last_page, # 마지막 페이지, page 처리에 사용
    'comments': comments, # 가입인사 댓글
    'post': post, # 가입인사 게시글
    'commentable': not is_greeted, # 가입인사를 했는지 여부
  })

# 후기 게시판
# 후기 게시판에는, 주간, 월간, 데일리 베스트 후기 게시글 정보가 표시됨, 각 베스트 게시글은 10개씩 표시
# 후기 게시글은 이미지가 1개 이상 포함됨.
# 후기 게시글은 target_post가 존재.
# 후기 게시글의 순위를 나타내는 weight는 스케줄러에서 관리함.
def review(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree(contexts['account']['account_type']) # 게시판 정보

  # 후기 게시판
  b = models.BOARD.objects.filter(board_type='review').first()
  board = {
    'id': b.id,
    'name': b.name,
  }

  '''
  # 데이터 가져오기
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')

  # search posts
  posts = models.POST.objects.select_related('author', 'review_post').prefetch_related('boards').filter(
    Q(title__contains=search) | Q(review_post__title__contains=search),
    boards__id__in=[str(b.id)],
  ).order_by('-created_at')
  last_page = len(posts) // 20 + 1
  posts = [{
    'id': p.id,
    'title': p.title,
    'image': '/media/' + str(p.image) if p.image else '/media/default.png',
    'view_count': p.view_count,
    'like_count': p.like_count,
    'created_at': p.created_at,
    'author': {
      'id': p.author.id,
      'nickname': p.author.first_name, # 작성자 닉네임
    },
    'review_post': { # 리뷰 게시글인 경우, 리뷰 대상 게시글 정보
      'id': p.review_post.id,
      'title': p.review_post.title,
    } if p.review_post else None,
  } for p in posts[(page - 1) * 20:page * 20]]

  today_best_reviews = None
  weekly_best_reviews = None
  monthly_best_reviews = None
  if page == 1:
    # best reviews
    # 오늘의 베스트 후기(추천, 조회, 업로드 순)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    today_best_reviews = []
    tbrs = models.POST.objects.select_related('author', 'review_post').prefetch_related('boards').filter(
      boards__id__in=[str(b.id)],
      created_at__date=today,
    ).order_by('-like_count', '-view_count', '-created_at')[:10]
    for tbr in tbrs:
      today_best_reviews.append({
        'id': tbr.id,
        'title': tbr.title,
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
    # 주간 베스트 후기(weight 기준)
    weekly_best_reviews = []
    wbrs = models.POST.objects.select_related('author', 'review_post').prefetch_related('boards').filter(
      boards__id__in=[str(b.id)],
      created_at__gte=datetime.datetime.now() - datetime.timedelta(days=7),
    ).order_by('-search_weight')[:10]
    for wbr in wbrs:
      weekly_best_reviews.append({
        'id': wbr.id,
        'title': wbr.title,
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
    # 월간 베스트 후기(weight 기준)
    now = datetime.datetime.now()
    monthly_best_reviews = []
    mbrs = models.POST.objects.select_related('author', 'review_post').prefetch_related('boards').filter(
      boards__id__in=[str(b.id)],
      created_at__year=now.year,
      created_at__month=now.month,
    ).order_by('-search_weight')[:10]
    for mbr in mbrs:
      monthly_best_reviews.append({
        'id': mbr.id,
        'title': mbr.title,
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
    '''

  return render(request, 'post/review.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 후기 게시판
    #'posts': posts, # 후기 게시글
    'last_page': 1, # 마지막 페이지, page 처리에 사용
    #'today_reviews': today_best_reviews, # 오늘의 베스트 후기
    #'weekly_reviews': weekly_best_reviews, # 주간 베스트 후기
    #'monthly_reviews': monthly_best_reviews, # 월간 베스트 후기
  })

# 후기 게시글 상세
def review_view(request):
  # account, activities(5), unread_messages(5), coupons(5), server, best_reviews(5)
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree(contexts['account']['account_type']) # 게시판 정보

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
  boards = daos.make_board_tree(contexts['account']['account_type']) # 게시판 정보

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids')
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')
  category = request.GET.get('category')

  # 게시판 가져오기
  board_ids = board_ids.split(',')
  board = daos.select_board(board_ids[-1]) # 마지막 게시판 정보 가져오기

  # 게시글 가져오기
  posts, last_page = daos.search_posts(
    title=search,
    category_id=category,
    board_id=board_ids[-1],
    page=page,
    post_type='travel',
    order='best',
  )

  # 카테고리 정보 가져오기
  categories = daos.make_category_tree()
  if category:
    category = daos.select_category(category)
  else:
    category = None

  return render(request, 'post/travel.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 게시판 정보
    'posts': posts, # 게시글 정보
    'last_page': last_page, # 마지막 페이지
    'categories': categories, # 카테고리 정보
    'category': category, # 카테고리 정보
  })

# 여행 게시글 상세보기
def travel_view(request):
  # account, activities(5), unread_messages(5), coupons(5), server, best_reviews(5)
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree(contexts['account']['account_type']) # 게시판 정보

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

  # 현재 사용자의 북마크에 추가된 게시글인지 확인
  if models.ACCOUNT.objects.prefetch_related('bookmarked_places').filter(
    username = contexts['account']['id'],
    bookmarked_places__id = post['id']
  ).exists():
    bookmarkable = False
  else:
    bookmarkable = True

  # 댓글 작성 가능 여부
  commentable = False
  if contexts['account']['account_type'] in post['boards'][-1]['comment']:
    commentable = True

  return render(request, 'post/travel_view.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'post': post, # 게시글 정보
    'bookmarkable': bookmarkable, # 북마크 가능 여부
    'comments': comments, # 댓글 정보
    'commentable': commentable, # 댓글 작성 가능 여부
  })

# 쿠폰 게시판
def coupon(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree(contexts['account']['account_type']) # 게시판 정보

  # 쿠폰 게시판
  b = models.BOARD.objects.filter(board_type='coupon').first()
  board = {
    'id': b.id,
    'name': b.name,
  }

  return render(request, 'post/coupon.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 쿠폰 게시판
    'writable': False, # 쿠폰 작성 가능 여부
    'last_page': 1, # 마지막 페이지, page 처리에 사용
  })