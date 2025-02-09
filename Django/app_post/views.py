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
  # account, activities(5), unread_messages(5), coupons(5), server, best_reviews(5)
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree(contexts['account']['account_type']) # 게시판 정보

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
    if contexts['account']['account_type'] not in board['enter']: # enter 권한 확인
      return redirect('/?redirect_message=not_allowed_board') # 권한이 없는 경우, 메인 페이지로 이동
    if contexts['account']['account_type'] in board['write']:
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
  # account, activities(5), unread_messages(5), coupons(5), server, best_reviews(5)
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree(contexts['account']['account_type']) # 게시판 정보

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids')
  review_post_id = request.GET.get('review_post_id')

  # board_ids가 없는 경우, 메인 페이지로 이동
  if not board_ids and not review_post_id:
    return redirect('/?redirect_message=not_found_board')
  board_ids = str(board_ids).split(',') # 게시판 아이디를 리스트로 변환

  # 게시판 접근 권한 확인
  if review_post_id: # 후기 게시글 작성인 경우
    if contexts['account']['account_type'] not in ['user', 'dame']: # 사용자, 파트너 계정만 가능
      return redirect('/?redirect_message=not_allowed_board')
    board_ids = [str(models.BOARD.objects.filter(board_type='review').first().id)]
  else:
    selected_boards = daos.get_selected_board_info(board_ids) # 선택된 게시판 정보
    for board in selected_boards:
      if contexts['account']['account_type'] not in board['write']: # write 권한 확인
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
    review_post_id = request.POST.get('review_post_id') # 후기 게시글 작성시, 대상 게시글 아이디
    image = request.FILES.get('image') if request.FILES.get('image') else None
    review_post_id = request.POST.get('review_post_id') # 후기 게시글 작성시, 대상 게시글 아이디
    board_ids = request.GET.get('board_ids') # 게시판 아이디
    if not title or not content: # 제목 또는 내용이 없는 경우
      return JsonResponse({'result': 'error'})
    board_ids = [int(b) for b in board_ids.split(',')]
    boards = models.BOARD.objects.filter(id__in=board_ids)
    if not boards:
      return JsonResponse({'result': 'error'})

    # 게시글 작성
    post = models.POST.objects.create(
      author=request.user,
      title=title,
      content=content,
      image=image,
    )
    post.boards.add(*boards)
    if review_post_id:
      review_post = models.POST.objects.filter(id=review_post_id).first()
      if review_post:
        post.review_post = review_post
    post.save()

    # 사용자 활동 기록 추가 및 포인트
    # 사용자 계정 및 파트너 계정만 해당
    if review_post_id:
      models.ACTIVITY.objects.create(
        account=request.user,
        message = f'[후기] {title} 후기를 작성하였습니다.',
      )
      point = int(models.SERVER_SETTING.objects.get(name='review_point').value)
    else:
      models.ACTIVITY.objects.create(
        account=request.user,
        message = f'[게시글] {title} 게시글을 작성하였습니다.',
      )
      point = int(models.SERVER_SETTING.objects.get(name='post_point').value)
    if contexts['account']['account_type'] in ['user', 'dame']:
      request.user.exp += point
      request.user.mileage += point
      request.user.save()

    # 레벨업
    daos.check_level_up(request.user.username)

    return JsonResponse({'result': 'success', 'post_id': post.id})

  # 후기 게시글인 경우
  if review_post_id:
    review_post_info = models.POST.objects.filter(id=review_post_id).first()
    review_post = {
      'id': review_post_info.id,
      'title': review_post_info.title,
    }
  else:
    review_post = None

  return render(request, 'post/write_post.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 게시판 정보
    'review_post': review_post, # 후기 게시글 정보
    'board_ids': ','.join([str(b) for b in board_ids]), # 게시판 아이디
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
    content = request.POST.get('content')
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
  # account, activities(5), unread_messages(5), coupons(5), server, best_reviews(5)
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree(contexts['account']['account_type']) # 게시판 정보

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
  post = daos.get_post_info(post_id)

  # 댓글 권한 확인
  commentable = False
  if contexts['account']['account_type'] in post['boards'][-1]['comment']:
    commentable = True

  # 마지막 게시판 가져오기
  board = post['boards'][-1]

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
    'board': board, # 게시판 정보
    'post': post, # 게시글 정보
    'commentable': commentable, # 댓글 작성 가능 여부
    'comments': comments, # 댓글 정보
  })

# 출석체크 게시판
def attendance(request):
  # account, activities(5), unread_messages(5), coupons(5), server, best_reviews(5)
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree(contexts['account']['account_type']) # 게시판 정보

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
    **contexts, # 기본 컨텍스트 정보
    'boards': boards, # 게시판 정보
    'comments': comments, # 출석 체크 글
    'post': post, # 출석체크 게시글
    'board': board, # 출석체크 게시판
    'attend_days': attend_days, # 이번달에 출석체크한 날짜
    'is_attended': is_attended, # 오늘 출석체크를 했는지 여부
  })

# 가입인사 게시판
def greeting(request):
  # account, activities(5), unread_messages(5), coupons(5), server, best_reviews(5)
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree(contexts['account']['account_type']) # 게시판 정보

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
    boards__id__in=str(b.id),
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
  comments = daos.get_all_post_comments(post.id)
  for comment in comments:
    if comment['author']['id'] == contexts['account']['id']:
      is_greeted = True
      break
  last_page = len(comments) // 20 + 1
  comments = comments[(page - 1) * 20:page * 20]

  return render(request, 'post/greeting.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'last_page': last_page, # 마지막 페이지, page 처리에 사용
    'comments': comments, # 가입인사 댓글
    'post': post, # 가입인사 게시글
    'is_greeted': is_greeted, # 가입인사를 했는지 여부
  })

# 후기 게시판
# 후기 게시판에는, 주간, 월간, 데일리 베스트 후기 게시글 정보가 표시됨, 각 베스트 게시글은 10개씩 표시
# 후기 게시글은 이미지가 1개 이상 포함됨.
# 후기 게시글은 target_post가 존재.
# 후기 게시글의 순위를 나타내는 weight는 스케줄러에서 관리함.
def review(request):
  # account, activities(5), unread_messages(5), coupons(5), server, best_reviews(5)
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree(contexts['account']['account_type']) # 게시판 정보

  # 후기 게시판
  b = models.BOARD.objects.filter(board_type='review').first()
  board = {
    'id': b.id,
    'name': b.name,
  }

  # 데이터 가져오기
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')

  # search posts
  posts, last_page = daos.get_board_posts(str(b.id), page, search)

  today_best_reviews = None
  weekly_best_reviews = None
  monthly_best_reviews = None
  if page == 1 and search == '':
    # best reviews
    # 오늘의 베스트 후기(추천, 조회, 업로드 순)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    today_best_reviews = []
    tbrs = models.POST.objects.select_related('author', 'review_post').filter(
      boards__id__in=str(b.id),
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
    wbrs = models.POST.objects.select_related('author', 'review_post').filter(
      boards__id__in=str(b.id),
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
    mbrs = models.POST.objects.select_related('author', 'review_post').filter(
      boards__id__in=str(b.id),
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

  return render(request, 'post/review.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 후기 게시판
    'posts': posts, # 후기 게시글
    'last_page': last_page, # 마지막 페이지, page 처리에 사용
    'today_reviews': today_best_reviews, # 오늘의 베스트 후기
    'weekly_reviews': weekly_best_reviews, # 주간 베스트 후기
    'monthly_reviews': monthly_best_reviews, # 월간 베스트 후기
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
  # account, activities(5), unread_messages(5), coupons(5), server, best_reviews(5)
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree(contexts['account']['account_type']) # 게시판 정보

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids')
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')
  category = request.GET.get('category', '')

  # 게시글 가져오기
  posts = []
  ps = models.POST.objects.select_related('place_info').prefetch_related('place_info__categories').exclude(
    Q(place_info__status='writing') | Q(place_info__status='blocked'), # place_info의 status가 'writing' 또는 'deleted'인 경우
    place_info__isnull=True, # 장소 정보가 없는 경우
  ).filter(
    title__contains=search, # 검색어가 제목에 포함된 경우
  )
  if category:
    ps.filter(
      place_info__categories__name=category
    )
  ps.order_by('search_weight')
  last_page = (ps.count() // 20) + 1
  ps = ps[(page - 1) * 20:page * 20] # 각 페이지에 20개씩 표시
  for p in ps:
    try:
      posts.append({
        'id': p.id,
        'title': p.title,
        'image': str(p.image) if p.image else '/media/default.png',
        'place_info': {
          'categories': [c.name for c in p.place_info.categories.all()],
          'address': p.place_info.address,
          'location_info': p.place_info.location_info,
          'open_info': p.place_info.open_info,
          'status': p.place_info.status,
        }
      })
    except:
      pass

  # 게시판 정보 가져오기(마지막 게시판 정보)
  board = models.BOARD.objects.filter(id=board_ids[-1]).first()

  # 카테고리 정보 가져오기
  categories = daos.get_category_tree()

  return render(request, 'post/travel.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'board': board, # 게시판 정보
    'posts': posts, # 게시글 정보
    'last_page': last_page, # 마지막 페이지
    'categories': categories, # 카테고리 정보
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
  print(post['boards'][-1]['comment'])
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
