import datetime
from django.http import JsonResponse
from django.shortcuts import redirect, render
from app_core import models
from app_core import daos



# 게시판 페이지
def poat_board(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids') # 게시판 아이디
  search = request.GET.get('search') # 검색어
  page = int(request.GET.get('page', '1')) # 페이지
  board = daos.select_board(str(board_ids).split(',')[-1]) # 마지막 게시판 정보 가져오기

  # 리다이렉트
  if not board_ids: # 게시판 아이디가 없는 경우
    return redirect('/?redirect_message=not_found_board') # 게시판이 없는 경우, 메인 페이지로 이동
  if not board: # 게시판이 없는 경우
    return redirect('/?redirect_message=not_found_board') # 게시판이 없는 경우, 메인 페이지로 이동
  if board['board_type'] == 'attendance': # 출석체크 게시판인 경우
    return redirect('/post/attendance?board_ids=' + board_ids)
  elif board['board_type'] == 'greeting': # 가입인사 게시판인 경우
    return redirect('/post/greeting?board_ids=' + board_ids)
  elif board['board_type'] == 'review': # 후기 게시판인 경우
    return redirect('/post/review?board_ids=' + board_ids)
  elif board['board_type'] == 'travel': # 여행지 게시판인 경우
    return redirect('/post/travel?board_ids=' + board_ids)
  if contexts['account']['account_type'] not in board['display_groups']: # display_groups 권한 확인
    return redirect('/?redirect_message=not_allowed_board') # 권한이 없는 경우, 메인 페이지로 이동
  if board['level_cut'] > contexts['account']['level']['level']: # 레벨 제한 확인
    return redirect('/?redirect_message=not_enough_level') # 레벨이 부족한 경우, 메인 페이지로 이동

  # 게시글 작성 가능 여부
  writable = False
  if contexts['account']['account_type'] in board['write_groups']:
    writable = True

  # 게시글 가져오기
  posts, last_page = daos.select_posts(
    title=search,
    board_id=board['id'],
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

# 출석체크 게시판
def attendance(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids') # 게시판 아이디
  board = daos.select_board(str(board_ids).split(',')[-1]) # 마지막 게시판 정보 가져오기

  # 리다이렉트
  if not request.user.is_authenticated: # 로그인이 안된 경우
    return redirect('/?redirect_message=need_login') # 로그인 페이지로 이동
  if board['board_type'] != 'attendance': # 출석체크 게시판이 아닌 경우
    return redirect('/?redirect_message=not_found_board') # 출석체크 게시판이 아닌 경우, 메인 페이지로 이동

  # 출석 체크 게시플 가져오기
  today = datetime.datetime.now().strftime('%Y-%m-%d')
  posts = models.POST.objects.filter(
    title__contains='attendance:' + today,
    boards__id__in=[board['id']],
  ).first()
  if not posts: # 만약 오늘의 출석체크 게시긇이 없다면, 생성
    post = daos.create_post(
      title='attendance:' + today,
      content='',
      board_ids=board_ids,
    )
    post_id = post['pk']
  else:
    post_id = posts.id

  # 댓글 가져오기
  comments = daos.select_comments(post_id)

  # 사용자가 이전에 출석한 날짜 가져오기
  is_attended = False
  attend_days = []
  monthPosts = models.POST.objects.filter(
    title__contains=f'attendance:{datetime.datetime.now().strftime("%Y-%m")}', # 이번달 출석체크 게시글
  )
  for post in monthPosts:
    attend = models.COMMENT.objects.filter(
      post=post,
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

    'board': board, # 출석체크 게시판
    'post': post, # 출석체크 게시글
    'comments': comments, # 출석 체크 글
    'attend_days': attend_days, # 이번달에 출석체크한 날짜
    'attend_point': attend_point, # 출석체크 포인트
    'commentable': not is_attended, # 오늘 출석체크를 했는지 여부
  })

# 가입인사 게시판
def greeting(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  page = int(request.GET.get('page', '1'))
  board_ids = request.GET.get('board_ids') # 게시판 아이디
  board = daos.select_board(str(board_ids).split(',')[-1]) # 마지막 게시판 정보 가져오기

  # 권한 확인
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=need_login') # 게스트는 가입인사 게시판 접근 불가
  if not board: # 게시판이 없는 경우
    return redirect('/?redirect_message=not_found_board') # 메인 페이지로 이동
  if board['board_type'] != 'greeting': # 가입인사 게시판이 아닌 경우
    return redirect('/?redirect_message=not_found_board') # 메인 페이지로 이동

  # 가입인사 게시글 가져오기
  post = models.POST.objects.filter(
    title='greeting',
    boards__id__in=[board['id']],
  ).first()
  if not post: # 가입인사 게시글이 없는 경우
    post = daos.create_post(
      title='greeting',
      content='',
      board_ids=board_ids,
    )
    post_id = post['pk']
  else:
    post_id = post.id

  # 가입인사 댓글 가져오기
  is_greeted = False
  comments = daos.select_comments(post_id)
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
    'post': post, # 가입인사 게시글
    'last_page': last_page, # 마지막 페이지, page 처리에 사용
    'comments': comments, # 가입인사 댓글
    'commentable': not is_greeted, # 가입인사를 했는지 여부
  })

# 후기 게시판
def review(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids') # 게시판 아이디
  board = daos.select_board(str(board_ids).split(',')[-1]) # 마지막 게시판 정보 가져오기
  search = request.GET.get('search', '') # 검색어
  related_post_id = request.GET.get('related_post_id') # 후기 게시글 대상 게시글 아이디
  page = int(request.GET.get('page', '1')) # 페이지

  # 게시글 검색
  posts, last_page = daos.select_posts(
    title=search,
    board_id=board['id'],
    related_post_id=related_post_id,
    page=page,
  )

  # 베스트 후기 정보
  today_best_reviews = None
  weekly_best_reviews = None
  monthly_best_reviews = None
  if page == 1:
    # best reviews
    # 오늘의 베스트 후기(추천, 조회, 업로드 순)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    today_best_reviews = []
    tbrs = models.POST.objects.select_related('author').filter(
      boards__id__in=[board['id']],
      created_at__date=today,
    ).order_by('-like_count', '-view_count', '-created_at')[:10]
    for tbr in tbrs:
      today_best_reviews.append({
        'id': tbr.id,
        'title': tbr.title,
        'author': {
          'id': tbr.author.id,
          'nickname': tbr.author.first_name,
        },
        'like_count': tbr.like_count,
        'view_count': tbr.view_count,
        'comment_count': models.COMMENT.objects.filter(post=tbr).count(),
        'created_at': datetime.datetime.strftime(tbr.created_at, '%Y-%m-%d %H:%M'),
      })
    # 주간 베스트 후기(weight 기준)
    weekly_best_reviews = []
    wbrs = models.POST.objects.select_related('author').filter(
      boards__id__in=[board['id']],
      created_at__gte=datetime.datetime.now() - datetime.timedelta(days=7),
    ).order_by('-search_weight')[:10]
    for wbr in wbrs:
      weekly_best_reviews.append({
        'id': wbr.id,
        'title': wbr.title,
        'author': {
          'id': wbr.author.id,
          'nickname': wbr.author.first_name,
        },
        'like_count': wbr.like_count,
        'view_count': wbr.view_count,
        'comment_count': models.COMMENT.objects.filter(post=wbr).count(),
        'created_at': datetime.datetime.strftime(wbr.created_at, '%Y-%m-%d %H:%M'),
      })
    # 월간 베스트 후기(weight 기준)
    now = datetime.datetime.now()
    monthly_best_reviews = []
    mbrs = models.POST.objects.select_related('author').filter(
      boards__id__in=[str(board['id'])],
      created_at__year=now.year,
      created_at__month=now.month,
    ).order_by('-search_weight')[:10]
    for mbr in mbrs:
      monthly_best_reviews.append({
        'id': mbr.id,
        'title': mbr.title,
        'author': {
          'id': mbr.author.id,
          'nickname': mbr.author.first_name,
        },
        'like_count': mbr.like_count,
        'view_count': mbr.view_count,
        'comment_count': models.COMMENT.objects.filter(post=mbr).count(),
        'created_at': datetime.datetime.strftime(mbr.created_at, '%Y-%m-%d %H:%M'),
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

# 여행 게시판
def travel(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids')
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')
  category_ids = request.GET.get('category_ids')
  board = daos.select_board(str(board_ids).split(',')[-1]) # 마지막 게시판 정보 가져오기
  if category_ids:
    category = daos.select_category(str(category_ids).split(',')[-1]) # 마지막 카테고리 정보 가져오기
  else:
    category = None

  # 게시글 가져오기
  posts, last_page = daos.select_posts(
    title=search,
    category_id=category['id'] if category else None,
    board_id=board['id'],
    page=page,
    post_type='travel',
    order='best',
  )

  # 카테고리 정보 가져오기
  categories = daos.make_category_tree()

  return render(request, 'post/travel.html', {
    **contexts,
    'boards': boards, # 게시판 정보

    'categories': categories, # 카테고리 정보
    'board': board, # 게시판 정보
    'category': category, # 카테고리 정보
    'posts': posts, # 게시글 정보
    'last_page': last_page, # 마지막 페이지
  })

# 게시글 작성 페이지
def write_post(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  board_ids = request.GET.get('board_ids') # 게시판 아이디
  related_post_id = request.GET.get('related_post_id') # 후기 게시글 대상 또는 쿠폰 게시글 대상 게시글 아이디
  board = daos.select_board(str(board_ids).split(',')[-1]) # 마지막 게시판 정보 가져오기

  # 리다이렉트
  if not request.user.is_authenticated: # 로그인이 안된 경우
    return redirect('/?redirect_message=need_login') # 로그인 페이지로 이동
  if not board_ids: # 게시판 아이디가 없는 경우
    return redirect('/?redirect_message=not_found_board') # 게시판이 없는 경우, 메인 페이지로 이동
  if int(contexts['account']['level']['level']) < int(board['level_cut']): # 레벨 제한 확인
    return redirect('/?redirect_message=not_enough_level') # 레벨이 부족한 경우, 메인 페이지로 이동

  # 게시글 작성 처리 요청
  if request.method == 'POST' and contexts['account']['account_type'] in board['write_groups']:
    # 데이터 가져오기
    title = request.POST.get('title')
    content = request.POST.get('content')
    image = request.FILES.get('image')
    if not title or not content: # 제목 또는 내용이 없는 경우
      return JsonResponse({'result': 'error'})
    coupon_name = request.POST.get('coupon_name')
    # 게시글 작성
    post = daos.create_post(
      author_id=request.user.id,
      title=title,
      content=content,
      board_ids=board_ids,
      related_post_id=related_post_id,
      image=image,
      include_coupon_name=coupon_name,
    )
    # 사용자 활동 기록 추가 및 포인트
    if board['board_type'] == 'review':
      point = int(models.SERVER_SETTING.objects.get(name='review_point').value)
      daos.create_account_activity(
        account_id=request.user.id,
        message=f'[후기] {title} 후기를 작성하였습니다.',
        exp_change=point,
        mileage_change=point,
      )
      daos.update_account(
        account_id=request.user.id,
        exp=request.user.exp + point,
        mileage=request.user.mileage + point,
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

  return render(request, 'post/write_post.html', {
    **contexts,
    'boards': boards, # 게시판 정보

    'board': board, # 게시판 정보
  })

# 게시글 수정 페이지
def rewrite_post(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  post_id = request.GET.get('post_id')
  board_ids = request.GET.get('board_ids')
  post = daos.select_post(post_id)
  board = daos.select_board(str(board_ids).split(',')[-1]) # 마지막 게시판 정보 가져오기

  # 리다이렉트
  if not request.user.is_authenticated: # 로그인이 안된 경우
    return redirect('/?redirect_message=need_login') # 로그인 페이지로 이동
  if not post: # 게시글이 없는 경우
    return redirect('/?redirect_message=not_found_post') # 메인 페이지로 이동
  if post['author']['id'] != contexts['account']['id']: # 작성자가 아닌 경우
    if not 'post' in contexts['account']['subsupervisor_permissions']:
      return redirect('/?redirect_message=not_allowed') # 권한이 없는 경우, 메인 페이지로 이동

  # 업데이트 요청 처리
  if request.method == 'POST':
    # 데이터 가져오기
    title = request.POST.get('title')
    content = request.POST.get('content')
    image = request.FILES.get('image')
    if not title or not content: # 제목 또는 내용이 없는 경우
      return JsonResponse({'result': 'error'})
    # 게시글 수정
    post = daos.update_post(
      post_id=post_id,
      title=title,
      content=content,
      image=image,
    )
    # 사용자 활동 기록 추가
    if board['board_type'] == 'review':
      daos.create_account_activity(
        account_id=request.user.id,
        message=f'[후기] {title} 후기를 수정하였습니다.',
      )
    else:
      daos.create_account_activity(
        account_id=request.user.id,
        message=f'[게시글] {title} 게시글을 수정하였습니다.',
      )
    return JsonResponse({'result': 'success', 'post_id': post['pk']})

  return render(request, 'post/rewrite_post.html', {
    **contexts, # 기본 컨텍스트 정보
    'boards': boards, # 게시판 정보

    'post': post, # 게시글 정보
    'board': post['boards'][-1], # 게시판 정보
  })

# 게시글 상세 페이지
def post_view(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 데이터 가져오기
  post_id = request.GET.get('post_id')
  post = daos.select_post(post_id)

  # 리다이렉트
  if not post: # 게시글이 없는 경우
    return redirect('/?redirect_message=not_found_post') # 메인 페이지로 이동
  if post['boards'][-1]['level_cut'] > contexts['account']['level']['level']: # 레벨 제한 확인
    return redirect('/?redirect_mssage=not_enough_level') # 레벨이 부족한 경우, 메인 페이지로 이동

  # 배너
  banners = daos.select_banners('post')

  # 댓글 권한 확인
  commentable = False
  if contexts['account']['account_type'] in post['boards'][-1]['comment_groups']:
    commentable = True

  # 댓글 가져오기
  comments = daos.select_comments(post_id)

  # 좋아요 가능 여부
  likeable = True
  if post_id in request.session.get('like_post_ids', ''):
    likeable = False

  # 조회수 증가
  if post_id not in  request.session.get('view_posts', ''):
    request.session['view_posts'] = request.session.get('view_posts', '') + ',' + post_id
    daos.update_post(
      post_id=post_id,
      view_count=post['view_count'] + 1,
    )

  return render(request, 'post/post_view.html', {
    **contexts,
    'boards': boards, # 게시판 정보

    'board': post['boards'][-1], # 게시판 정보
    'category': post['place_info']['categories'][-1] if post['place_info'] else None, # 카테고리 정보
    'post': post, # 게시글 정보
    'comments': comments, # 댓글 정보
    'commentable': commentable, # 댓글 작성 가능 여부
    'likeable': likeable, # 좋아요 가능 여부
    'banners': banners, # 배너 정보
  })
