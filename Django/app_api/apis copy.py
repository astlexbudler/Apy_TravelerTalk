import datetime
import random
import string
from django.http import JsonResponse
from django.contrib.auth import authenticate, logout, get_user_model, login
from django.contrib.auth.models import Group
from django.db.models import Q

from app_core import models
from app_core import daos

# 로그인 API
# POST: id, password
def account_login(request):
  if request.method == 'POST':

    # 아이디 및 비밀번호 확인
    id = request.POST.get('id', '')
    password = request.POST.get('password', '')
    user = authenticate(request, username=id, password=password)
    ip = request.META.get('REMOTE_ADDR')
    if models.BLOCKED_IP.objects.filter(ip=ip).exists():
      return JsonResponse({'result': 'error'})

    # 로그인 성공
    if user is not None:
      user.recent_ip = ip
      user.save()
      if user.status == 'active': # 활성화 상태
        login(request, user)
      elif 'pending' in user.status: # 승인 대기 상태
        login(request, user)
      return JsonResponse({'result': user.status})

    # 로그인 실패
  return JsonResponse({'result': 'error'})

# 로그아웃 API
def account_logout(request):
  logout(request)
  return JsonResponse({'result': 'success'})

# 파일 업로드 API
def upload(request):
  upload = models.UPLOAD(
    file = request.FILES["file"]
  )
  upload.save()
  path = "/media/" + str(upload.file)
  return JsonResponse({
      "path": path # 파일 업로드 후 경로 반환
  })

# 사용자 API
# POST-create: 사용자 정보 생성
# GET: 사용자 정보 검색
# POST-update: 사용자 정보 수정
# DELETE: 사용자 정보 삭제
def account(request):

  # 사용자 정보 생성
  if request.method == 'POST' and request.GET.get('create'):

    # 회원가입 정보 확인
    account_type = request.POST['account_type']
    id = request.POST['id']
    password = request.POST['password']
    nickname = request.POST['nickname']
    partner_name = request.POST.get('partner_name', '')
    email = request.POST.get('email', '')
    tel = request.POST.get('tel', '')
    address = request.POST.get('address', '') # place address
    service_category = request.POST.get('service_category', '') # category_ids
    location_category = request.POST.get('location_category', '') # board_ids

    # status
    if account_type == 'partner' or account_type == 'dame': # 파트너 또는 여성 회원일 경우
      status = 'pending'
      # 승인 대기는 관리자가 확인 후 활성화 가능.
      # 승인 대기 상태에서는 일부 기능 제한
      # 글 작성, 댓글 작성, 출석 불가
    else:
      status = 'active'

    # point
    if account_type == 'user' or account_type == 'dame': # 사용자 또는 여성 회원일 경우
      point = int(models.SERVER_SETTING.objects.get(name='register_point').value) # 가입 포인트 지급
    else:
      point = 0

    # 아이디 중복 확인
    id_exist = models.ACCOUNT.objects.filter(username=id).exists()
    nickname_exist = models.ACCOUNT.objects.filter(first_name=nickname).exists()
    if id_exist or nickname_exist:
      return JsonResponse({'result': 'exist'})

    # 회원가입
    account = models.ACCOUNT(
      username=id, # 아이디
      first_name=nickname, # 닉네임
      last_name=partner_name, # 파트너 업체명
      email=email, # 파트너 이메일
      status=status, # 계정 상태
      tel=tel, # 파트너 연락처
      mileage=point, # 쿠폰 포인트
      exp=point # 레벨업 포인트
    )
    account.set_password(password) # 비밀번호 설정
    account.save()
    account.level = models.LEVEL_RULE.objects.get(level=1) # 레벨 설정
    if account_type == 'partner':
      account.groups.add(Group.objects.get(name='partner'))
    elif account_type == 'dame':
      account.groups.add(Group.objects.get(name='dame'))
    elif account_type == 'user':
      account.groups.add(Group.objects.get(name='user'))
    account.save()

    # account_type이 partner인 경우, 여행지 게시글 프리셋 생성
    if account_type == 'partner':
      # 여행지 게시글 생성
      post = models.POST(
        author=account, # 작성자
        title=account.last_name + ' 여행지', # 제목
        content='파트너사 ' + account.last_name + '의 여행지 정보입니다.', # 내용
      )
      post.save()
      for b in [int(b) for b in str(location_category).split(',')]:
        board = models.BOARD.objects.filter(id=b).first()
        if board:
          post.boards.add(board)
      post.save()
      # 게시글 여행지 정보 생성
      place_info = models.PLACE_INFO(
        post=post, # 게시글
        address=address, # 주소
        location_info='여행지를 찾기위한 간단한 안내입니다.', # 위치 정보
        open_info='여행지의 영업 시간입니다.', # 영업 정보
        status='writing' # 상태
      )
      place_info.save()
      post.place_info = place_info
      post.save()
      for c in [int(c) for c in str(service_category).split(',')]:
        category = models.CATEGORY.objects.filter(id=c).first()
        if category:
          place_info.categories.add(category)
      place_info.save()

    # 회원가입 활동기록 생성
    if account_type == 'partner':
      models.ACTIVITY.objects.create(
        account=account,
        message = f'[계정] {nickname}님의 파트너사 계정을 생성했습니다.',
      )
    elif account_type == 'dame' or account_type == 'user':
      models.ACTIVITY.objects.create(
        account=account,
        message = f'[계정] {nickname}님의 계정을 생성했습니다.',
        mileage_change = '+' + str(point),
        exp_change = '+' + str(point),
      )

    # 레벨업
    daos.check_level_up(account.username)

    return JsonResponse({'result': status})

  # 사용자 정보 검색
  elif request.method == 'GET':
    id_or_nickname = request.GET.get('id_or_nickname', '')

    # 아이디 또는 닉네임으로 사용자 조회(일치 여부 확인)
    users = models.ACCOUNT.objects.filter(
      Q(username=id_or_nickname) | Q(first_name=id_or_nickname)
    )
    return JsonResponse({
      'users': [{
        'id': user.username,
        'nickname': user.first_name,
      } for user in users]
    })

  # 사용자 정보 수정
  elif request.method == 'POST' and request.GET.get('update'):

    if not request.user.is_authenticated: # 비로그인 상태인 경우, 에러 반환
      return JsonResponse({'result': 'error'})

    # 수정 대상 설정
    modifier = models.ACCOUNT.objects.prefetch_related('groups').filter(
      username=request.user.username
    ).first()
    modifier_groups = [group.name for group in modifier.groups.all()]
    modifier_type = 'user'
    if 'dame' in modifier_groups:
      modifier_type = 'dame'
    elif 'partner' in modifier_groups:
      modifier_type = 'partner'
    elif 'subsupervisor' in modifier_groups:
      modifier_type = 'subsupervisor'
    elif 'supervisor' in modifier_groups:
      modifier_type = 'supervisor'

    if 'supervisor' == modifier_type or ('subsupervisor' == modifier_type and 'user' in modifier.subsupervisor_permissions):
      id = request.POST.get('edit_account_id')
    else: # 그 외의 경우, 수정 대상을 로그인한 사용자로 설정
      id = request.user.username
    # 수정 대상 확인
    user = models.ACCOUNT.objects.get(username=id)

    # 정보 수정
    # 닉네임
    nickname = request.POST.get('nickname', user.first_name)
    user.first_name = nickname
    # 비밀번호
    password = request.POST.get('password', '')
    if password != '':
      user.set_password(password)
    # 파트너 업체명
    partner_name = request.POST.get('partner_name', user.last_name)
    user.last_name = partner_name
    # 이메일
    email = request.POST.get('email', user.email)
    user.email = email
    # 계정 상태
    status = request.POST.get('status', user.status)
    user.status = status
    # 관리자 메모
    note = request.POST.get('note', user.note)
    user.note = note
    # 마일리지
    mileage = int(request.POST.get('mileage', user.mileage))
    user.mileage = mileage
    # 레벨 경험치
    exp = int(request.POST.get('exp', user.exp))
    user.exp = exp
    # 연락처
    tel = request.POST.get('tel', user.tel)
    user.tel = tel
    # 권한
    subsupervisor_permissions = request.POST.get('subsupervisor_permissions', user.subsupervisor_permissions)
    user.subsupervisor_permissions = subsupervisor_permissions

    # 저장
    user.save()

    # 활동 기록 생성
    if 'supervisor' in modifier_groups or ('subsupervisor' in modifier_groups and 'user' in modifier.subsupervisor_permissions): # 관리자 계정일 경우,
      models.ACTIVITY.objects.create(
        account=user,
        message = f'[계정] {nickname}님의 계정 정보가 관리자에 의해 수정되었습니다.',
      )
    else: # 그 외의 경우,
      models.ACTIVITY.objects.create(
        account=user,
        message = f'[계정] {nickname}님의 계정 정보를 수정했습니다.',
      )

    # 레벨업
    daos.check_level_up(user.username)

    return JsonResponse({'success': 'y'})

  # 사용자 정보 삭제
  elif request.method == 'DELETE':

    if not request.user.is_authenticated: # 비로그인 상태인 경우, 에러 반환
      return JsonResponse({'result': 'error'})

    # 삭제 대상 설정
    deleter = models.ACCOUNT.objects.prefetch_related('groups').first()
    deleter_groups = [group.name for group in deleter.groups.all()]
    deleter_type = 'user'
    if 'dame' in deleter_groups:
      deleter_type = 'dame'
    elif 'partner' in deleter_groups:
      deleter_type = 'partner'
    elif 'subsupervisor' in deleter_groups:
      deleter_type = 'subsupervisor'
    elif 'supervisor' in deleter_groups:
      deleter_type = 'supervisor'

    if 'supervisor' == deleter_type or ('subsupervisor' == deleter_type and 'user' in deleter.subsupervisor_permissions):
      id = request.POST.get('delete_account_id')
    else: # 그 외의 경우, 삭제 대상을 로그인한 사용자로 설정
      id = request.user.username

    # 삭제 대상 확인
    user = models.ACCOUNT.objects.get(username=id)

    # 삭제
    user.status = 'deleted'
    user.save()
    # 이후 last_login이 90일 이상 지나면 DB에서 삭제됨.(scheduler로 구현)

    return JsonResponse({'success': 'y'})

# 메세지 API
# POST: 메세지 발송
# GET: 메세지 읽음 처리
def message(request):

  # 메세지 발송
  if request.method == 'POST':

    # 발신자 확인
    sender = models.ACCOUNT.objects.prefetch_related('groups').filter(
      username=request.user.username
    ).first()
    if not sender: # 발신자가 존재하지 않는 경우,
      guest_id = request.session.get('guest_id', ''.join(random.choices(string.ascii_letters + string.digits, k=16)))
      request.session['guest_id'] = guest_id
      sender_id = guest_id
    else: # 발신자가 존재하는 경우,
      sender_groups = [group.name for group in sender.groups.all()]
      account_type = 'guest'
      if sender: # 발신자가 존재하는 경우
        account_type = 'user'
        if 'dame' in sender_groups:
          account_type = 'dame'
        elif 'partner' in sender_groups:
          account_type = 'partner'
        elif 'subsupervisor' in sender_groups:
          account_type = 'subsupervisor'
        elif 'supervisor' in sender_groups:
          account_type = 'supervisor'

      # 발신자 아이디 설정
      if account_type == 'guest':
        sender_id = request.session.get('guest_id', ''.join(random.choices(string.ascii_letters + string.digits, k=16)))
        request.session['guest_id'] = sender_id
      elif account_type == 'supervisor' or account_type == 'subsupervisor':
        sender_id = 'supervisor'
      else:
        sender_id = sender.username

    # 쪽지 내용 설정
    to_id = request.POST.get('to_id') # 수신자 아이디
    title = request.POST.get('title') # 제목
    content = request.POST.get('content') # 내용
    coupon_code = request.POST.get('coupon_code') # 쿠폰 포함 여부(쿠폰은 쪽지를 통해 전달 가능)
    image = request.FILES.get('image') # 이미지

    # 쪽지 확인
    if not title or not content: # 제목 또는 내용이 없는 경우, 에러 반환
      return JsonResponse({'result': 'error'})

    # 쪽지 저장
    message = models.MESSAGE.objects.create(
      to_account=to_id,
      sender_account=sender_id,
      image = image,
      title = title,
      content = content,
    )
    if coupon_code: # 쿠폰 코드가 있는 경우, 쿠폰 저장
      coupon = models.COUPON.objects.filter(code=coupon_code).first()
      if coupon:
        message.include_coupon = coupon
    message.save()

    # 쪽지 발송 활동기록 생성
    if request.user.is_authenticated: # 로그인 상태인 경우

      # 관리자에게 보낸 경우, receiver를 '관리자'로 설정
      if to_id == 'supervisor':
        receiver = '관리자'
      else:
        receiver = get_user_model().objects.get(username=to_id).first_name

      activity = models.ACTIVITY(
        account=request.user,
        message = f'[쪽지] {receiver}님에게 쪽지를 보냈습니다.',
      )
      activity.save()

    return JsonResponse({
      'result': 'success',
      'message_id': message.id
    })

  # 메세지 읽음 처리
  elif request.method == 'GET':

    message_id = request.GET.get('message_id', '')
    message = models.MESSAGE.objects.filter(
      id=message_id
    ).first()
    if message:
      if not message.is_read:
        message.is_read = True
        message.save()

    return JsonResponse({'result': 'success'})

# 댓글 API
# POST: 댓글 작성
# DELETE: 댓글 삭제
def comment(request):

  # 댓글 작성
  if request.method == 'POST':
    post_id = request.POST.get('post_id')
    content = request.POST.get('content')

    if not post_id or not content: # 게시글 아이디 또는 내용이 없는 경우
      return JsonResponse({'result': 'empty'})

    # 게시글 확인
    po = models.POST.objects.prefetch_related('boards').prefetch_related('boards__comment_groups').filter(
      id=post_id
    ).first()
    if po is None: # 댓글을 작성할 게시긇이 없는 경우
      return JsonResponse({'result': 'empty'})

    # 댓글 작성
    models.COMMENT.objects.create(
      post=po,
      author=request.user,
      content=content,
    )

    # 만약 게시글이 출석 체크 게시글인 경우,
    if 'attendance:' in po.title:

      # 1등, 2등, 3등의 경우, 추가 포인트 지급
      if models.COMMENT.objects.filter(post=po).count() == 1:
        add_point = int(models.SERVER_SETTING.objects.get(name='attend_point').value) * 2
      elif models.COMMENT.objects.filter(post=po).count() == 2:
        add_point = int(models.SERVER_SETTING.objects.get(name='attend_point').value) * 1.5
      elif models.COMMENT.objects.filter(post=po).count() == 3:
        add_point = int(models.SERVER_SETTING.objects.get(name='attend_point').value) * 1.2
      else:
        add_point = models.SERVER_SETTING.objects.get(name='attend_point').value

      # 댓글 작성 활동기록 생성
      today = datetime.datetime.now().strftime('%Y-%m-%d')
      models.ACTIVITY.objects.create(
        account=request.user,
        message = f'[출석체크] {today} 출석체크를 완료했습니다.',
        exp_change = add_point,
        mileage_change = add_point,
      )

    elif 'greeting' in po.title:

      add_point = models.SERVER_SETTING.objects.get(name='comment_point').value

      # 댓글 작성 활동기록 생성
      models.ACTIVITY.objects.create(
        account=request.user,
        message = f'[인사] 인사를 완료했습니다.',
        exp_change = add_point,
        mileage_change = add_point,
      )

    else: # 그 외의 경우,
      add_point = models.SERVER_SETTING.objects.get(name='comment_point').value

      # 댓글 작성 활동기록 생성
      models.ACTIVITY.objects.create(
        account=request.user,
        message = f'[게시판] {po.title} 게시글에 댓글을 작성했습니다.',
        exp_change = add_point,
        mileage_change = add_point,
      )

    request.user.mileage += int(add_point)
    request.user.exp += int(add_point)
    request.user.save()

    # 레벨업
    daos.check_level_up(request.user.username)

    return JsonResponse({'result': 'success'})

  if request.method == 'DELETE':
    comment_id = request.GET.get('comment_id', '')

    # 댓글 확인
    comment = models.COMMENT.objects.select_related('author').filter(
      id=comment_id
    ).first()
    if comment is None: # 댓글이 존재하지 않는 경우
      return JsonResponse({'result': 'comment_not_exist'})

    # 사용자 확인
    user = models.ACCOUNT.objects.prefetch_related('groups').filter(
      username=request.user.username
    ).first()
    user_groups = [group.name for group in user.groups.all()]

    # 관리자 또는 댓글 작성자만 삭제 가능
    if 'supervisor' in user_groups or ('subsupervisor' in user_groups and 'post' in user.subsupervisor_permissions):
      pass
    elif comment.author != user: # 댓글 작성자가 아닌 경우
      return JsonResponse({'result': 'permission_denied'})

    # 댓글 삭제
    comment.delete()

    return JsonResponse({'result': 'success'})

# 쿠폰 API
# POST-create: 쿠폰 생성
# GET: 쿠폰 검색
# POST-patch: 쿠폰 수정
def coupon(request):

  # 쿠폰 생성
  if request.method == 'POST' and request.GET.get('create'):

    # 쿠폰 정보 확인
    code = request.POST.get('code', '')
    name = request.POST.get('name', '')
    image = request.FILES.get('image')
    content = request.POST.get('content', '')
    required_mileage = int(request.POST.get('required_mileage', '0'))
    expire_at = request.POST.get('expire_at', '')
    post_id = request.POST.get('post_id', '')

    # 쿠폰 코드 중복 확인
    if models.COUPON.objects.filter(code=code).exists():
      return JsonResponse({'result': 'exist'})

    # 게시글 확인
    post = models.POST.objects.select_related('place_info').filter(
      Q(place_info__isnull=False) & Q(id=post_id)
    ).first()
    if not post: # 게시글이 존재하지 않는 경우
      return JsonResponse({'result': 'post_not_exist'})

    # 쿠폰 생성
    coupon = models.COUPON(
      code=code,
      name=name,
      content=content,
      image=image,
      required_mileage=required_mileage,
      expire_at=expire_at,
      post=post,
      create_account=request.user,
    )
    coupon.save()

    # 통계 데이터 생성
    coupon_create = models.STATISTIC.objects.filter(
      name='coupon_create',
      date=datetime.datetime.now().strftime('%Y-%m-%d')
    ).first()
    if coupon_create:
      coupon_create.value += 1
      coupon_create.save()
    else:
      models.STATISTIC.objects.create(
        name='coupon_create',
        value=1
      )

    return JsonResponse({'result': 'success'})

  # 쿠폰 검색
  if request.method == 'GET':

    # 쿠폰 코드로 쿠폰 조회
    coupon_code = request.GET.get('code', '')
    cp = models.COUPON.objects.filter(
      code=coupon_code,
      create_account=request.user
    ).first()

    if cp is None: # 쿠폰이 존재하지 않는 경우, not_exist 반환
      return JsonResponse({
        'result': 'not_exist',
      })

    # 쿠폰 정보 확인
    coupon = {
      'code': cp.code,
      'name': cp.name,
    }

    return JsonResponse({
      'result': 'success',
      'coupon': coupon
    })

  # 쿠폰 수정
  if request.method == 'POST' and request.GET.get('patch'):

    # 쿠폰 정보 확인
    code = request.POST.get('code', '')

    coupon = models.COUPON.objects.filter(
      code=code
    ).first()
    if not coupon: # 쿠폰이 존재하지 않는 경우
      return JsonResponse({'result': 'not_exist'})

    name = request.POST.get('name', coupon.name)
    content = request.POST.get('content', coupon.content)
    image = request.FILES.get('image', coupon.image)
    required_mileage = request.POST.get('required_mileage', coupon.required_mileage)
    expire_at = request.POST.get('expire_at', coupon.expire_at)
    status = request.POST.get('status', coupon.status)
    own_account_ids = request.POST.get('own_account_ids')
    used_account_ids = request.POST.get('used_account_ids')

    # 쿠폰 정보 수정
    coupon.name = name
    coupon.content = content
    if image:
      coupon.image = image
    coupon.required_mileage = required_mileage
    coupon.expire_at = expire_at
    coupon.status = status
    coupon.save()

    # 쿠폰 소유자 수정
    if own_account_ids:
      coupon.own_accounts.clear()
      for own_account_id in own_account_ids.split(','):
        account = models.ACCOUNT.objects.filter(username=own_account_id).first()
        if account:
          coupon.own_accounts.add(account)
    if used_account_ids:
    # 쿠폰 사용자 수정
      coupon.used_account.clear()
      for used_account_id in used_account_ids.split(','):
        account = models.ACCOUNT.objects.filter(username=used_account_id).first()
        if account:
          coupon.used_account.add(account)
      coupon.save()

    return JsonResponse({'result': 'success'})


# 아이디 중복 확인 API
def check_id(request):
  id = request.GET.get('id', '')
  User = get_user_model()

  # 아이디가 이미 존재하는 경우
  if User.objects.filter(username=id).exists():
    return JsonResponse({'result': 'exist'}) # exist 반환
  return JsonResponse({'result': 'not_exist'}) # not_exist 반환

# 닉네임 중복 확인 API(닉네임 == 파트너사 이름)
def check_nickname(request):
  nickname = request.GET.get('nickname', '')
  User = get_user_model()

  # 닉네임이 이미 존재하는 경우
  if User.objects.filter(first_name=nickname).exists():
    return JsonResponse({'result': 'exist'}) # exist 반환
  return JsonResponse({'result': 'not_exist'}) # not_exist 반환

# 쿠폰 사용자 API
# GET: 쿠폰 받기
# POST-use: 쿠폰 사용
# POST-cancel: 쿠폰 사용 취소
# POST-retrieve: 쿠폰 회수
def coupon_user(request):

  # 쿠폰 사용
  if request.method == 'POST' and request.GET.get('use'):

    # 쿠폰 정보 확인
    code = request.POST.get('code', '')
    coupon = models.COUPON.objects.select_related('create_account').prefetch_related('used_account', 'own_accounts').filter(
      code=code
    ).first()
    if not coupon: # 쿠폰이 존재하지 않는 경우
      return JsonResponse({'result': 'not_exist'})

    # 쿠폰 사용자 확인
    account_username = request.POST.get('account', '')
    own_accounts = [own_account.username for own_account in coupon.own_accounts.all()]
    if account_username not in own_accounts: # 쿠폰 소유자가 아닌 경우
      return JsonResponse({'result': 'permission_denied'})

    # 쿠폰 사용
    account = models.ACCOUNT.objects.filter(
      username=account_username
    ).first()
    account.mileage -= coupon.required_mileage
    if account.mileage < 0:
      return JsonResponse({'result': 'mileage_lack'})
    account.save()
    coupon.used_account.add(account)
    coupon.own_accounts.remove(account)
    coupon.save()

    # 쿠폰 사용 활동기록 생성
    models.ACTIVITY.objects.create(
      account=account,
      message = f'[쿠폰] {coupon.name} 쿠폰을 사용했습니다.',
      mileage_change = '-' + str(coupon.required_mileage),
    )
    models.ACTIVITY.objects.create(
      account=coupon.create_account,
      message = f'[쿠폰] {account_username}님이 {coupon.name} 쿠폰을 사용했습니다.',
    )

    # 통계 데이터 생성
    coupon_use = models.STATISTIC.objects.filter(
      name='coupon_use',
      date=datetime.datetime.now().strftime('%Y-%m-%d')
    ).first()
    if coupon_use:
      coupon_use.value += 1
      coupon_use.save()
    else:
      models.STATISTIC.objects.create(
        name='coupon_use',
        value=1
      )
    mileage_use = models.STATISTIC.objects.filter(
      name='mileage_use',
      date=datetime.datetime.now().strftime('%Y-%m-%d')
    ).first()
    if mileage_use:
      mileage_use.value += coupon.required_mileage
      mileage_use.save()
    else:
      models.STATISTIC.objects.create(
        name='mileage_use',
        value=coupon.required_mileage
      )

    return JsonResponse({'result': 'success'})

  # 쿠폰 사용 취소
  if request.method == 'POST' and request.GET.get('cancel'):

    # 쿠폰 정보 확인
    code = request.POST.get('code', '')
    coupon = models.COUPON.objects.filter(
      code=code
    ).first()
    if not coupon: # 쿠폰이 존재하지 않는 경우
      return JsonResponse({'result': 'not_exist'})

    # 쿠폰 사용자 확인
    account_username = request.POST.get('account', '')
    used_account = [used_account.username for used_account in coupon.used_account.all()]
    if account_username not in used_account: # 쿠폰 사용자가 아닌 경우
      return JsonResponse({'result': 'permission_denied'})

    # 쿠폰 사용 취소
    account = models.ACCOUNT.objects.filter(
      username=account_username
    ).first()
    account.mileage += coupon.required_mileage
    account.save()
    coupon.used_account.remove(account)
    coupon.own_accounts.add(account)
    coupon.save()

    # 쿠폰 사용 취소 활동기록 생성
    models.ACTIVITY.objects.create(
      account=account,
      message = f'[쿠폰] {coupon.name} 쿠폰 사용을 취소했습니다.',
      mileage_change = '+' + str(coupon.required_mileage),
    )
    models.ACTIVITY.objects.create(
      account=coupon.create_account,
      message = f'[쿠폰] {account_username}님이 {coupon.name} 쿠폰 사용을 취소했습니다.',
    )

    # 통계 데이터 생성
    coupon_use = models.STATISTIC.objects.filter(
      name='coupon_use',
      date=datetime.datetime.now().strftime('%Y-%m-%d')
    ).first()
    if coupon_use:
      coupon_use.value -= 1
      coupon_use.save()
    else:
      models.STATISTIC.objects.create(
        name='coupon_use',
        value=-1
      )
    mileage_use = models.STATISTIC.objects.filter(
      name='mileage_use',
      date=datetime.datetime.now().strftime('%Y-%m-%d')
    ).first()
    if mileage_use:
      mileage_use.value -= coupon.required_mileage
      mileage_use.save()
    else:
      models.STATISTIC.objects.create(
        name='mileage_use',
        value=-coupon.required_mileage
      )

    return JsonResponse({'result': 'success'})

  # 쿠폰 회수
  if request.method == 'POST' and request.GET.get('retrieve'):

    # 쿠폰 정보 확인
    code = request.POST.get('code', '')
    coupon = models.COUPON.objects.prefetch_related('own_accounts').filter(
      code=code
    ).first()
    if not coupon: # 쿠폰이 존재하지 않는 경우
      return JsonResponse({'result': 'not_exist'})

    # 쿠폰 회수
    account_username = request.POST.get('account', '')
    account = models.ACCOUNT.objects.filter(
      username=account_username
    ).first()
    coupon.own_accounts.remove(account)
    coupon.save()

    # 쿠폰 회수 활동기록 생성
    models.ACTIVITY.objects.create(
      account=account,
      message = f'[쿠폰] {coupon.name} 쿠폰이 회수되었습니다.',
    )

    return JsonResponse({'result': 'success'})

# 쿠폰 받기 api
def receive_coupon(request):
  message_id = request.GET.get('message_id', '')
  message = models.MESSAGE.objects.filter(
    id=message_id
  ).select_related('include_coupon').first()
  if message.to_account != request.user.username: # 수신자가 아닌 경우
    return JsonResponse({'result': 'permission_denied'})

  # 쿠폰 수신
  if message.include_coupon:
    coupon = message.include_coupon
    coupon.own_accounts.add(request.user)
    coupon.save()
    message.include_coupon = None
    message.save()

    # 쿠폰 수신 활동기록 생성
    models.ACTIVITY.objects.create(
      account=request.user,
      message = f'[쿠폰] {coupon.name} 쿠폰을 받았습니다.',
    )

  return JsonResponse({'result': 'success'})

# 게시글 좋아요
def like_post(request):
  # 게시글 아이디 확인
  post_id = request.GET.get('post_id', '')
  post = models.POST.objects.prefetch_related('boards').filter(
    id=post_id
  ).first()

  if not post: # 게시글이 존재하지 않는 경우
    return JsonResponse({'result': 'post_not_exist'})

  # 사용자 좋아요 확인
  like_posts = request.session.get('like_posts', '')
  if post_id not in like_posts: # 좋아요가 존재하지 않는 경우
    request.session['like_posts'] = like_posts + post_id + ',' # 좋아요 추가
    post.like_count += 1
    post.save()
  else:
    request.session['like_posts'] = like_posts.replace(post_id + ',', '') # 좋아요 삭제
    post.like_count -= 1
    post.save()

  # 게시글 확인
  board = post.boards.all().last()
  print('board.board_type:', board.board_type)
  if 'travel' == board.board_type: # 여행지 게시글인 경우, 북마크 추가
    user = models.ACCOUNT.objects.prefetch_related('bookmarked_places').filter(
      username=request.user.username
    ).first()
    bookmarked = models.ACCOUNT.objects.prefetch_related('bookmarked_places').filter(
      username=request.user.username,
      bookmarked_places=post
    ).exists()
    if not bookmarked:
      user.bookmarked_places.add(post)
      user.save()
    else:
      user.bookmarked_places.remove(post)
      user.save()

  return JsonResponse({'result': 'success'})
