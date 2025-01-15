import datetime
import random
import string
from django.http import JsonResponse
from django.contrib.auth import authenticate, logout, get_user_model, login
from django.db.models import Q

from app_core import models as core_mo
from app_user import models as user_mo
from app_partner import models as partner_mo
from app_supervisor import models as supervisor_mo
from app_post import models as post_mo
from app_message import models as message_mo
from app_coupon import models as coupon_mo

# 로그인 API
# POST: id, password
def account_login(request):
  if request.method == 'POST':

    # 아이디 및 비밀번호 확인
    id = request.POST.get('id', '')
    password = request.POST.get('password', '')
    user = authenticate(request, username=id, password=password)

    # 로그인 성공
    if user is not None:
      if user.status == 'active': # 활성화 상태
        login(request, user)
        return JsonResponse({'result': 'success'})
      elif user.status == 'pending': # 승인 대기 상태
        login(request, user)
        return JsonResponse({'result': 'pending'})
      elif user.status == 'sleeping': # 휴면 상태
        return JsonResponse({'result': 'sleeping'})
      elif user.status == 'banned': # 정지 상태
        return JsonResponse({'result': 'banned'})

    # 로그인 실패
  return JsonResponse({'result': 'error'})

# 로그아웃 API
def account_logout(request):
  logout(request)
  return JsonResponse({'result': 'success'})

# 회원가입 API
def signup(request):
  if request.method == 'POST':

    # 회원가입 정보 확인
    account_type = request.POST['account_type']
    id = request.POST['id']
    password = request.POST['password']
    nickname = request.POST['nickname']
    category = request.POST.get('category', '')
    tel = request.POST.get('tel', '')
    address = request.POST.get('address', '')
    status = 'active'
    point = 0

    # 파트너 또는 여성 회원일 경우
    if account_type == 'partner' or account_type == 'dame':
      status = 'pending' # 승인 대기 상태로 설정
      # 승인 대기는 관리자가 확인 후 활성화 가능.
      # 승인 대기 상태에서는 일부 기능 제한
      # 글 작성, 댓글 작성, 출석 불가

    # 사용자 또는 여성 회원일 경우
    if account_type == 'user' or account_type == 'dame':
      point = int(core_mo.SERVER_SETTING.objects.get(id='register_point').value) # 가입 포인트 지급

    # 아이디 중복 확인
    User = get_user_model()
    if User.objects.filter(username=id).exists() or User.objects.filter(first_name=nickname).exists():
      return JsonResponse({'result': 'exist'})

    # 회원가입
    account = User(
      username=id,
      first_name=nickname,
      status=status,
      account_type=account_type,
      user_usable_point=point,
      partner_categories=category,
      partner_tel=tel,
      partner_address=address
    )
    account.set_password(password)
    account.save()

    # 회원가입 활동기록 생성
    activity = user_mo.ACTIVITY(
      message = f'[계정] {nickname}님이 가입하셨습니다.',
      user_id = id,
      point_change = '+' + str(point),
    )
    activity.save()

    return JsonResponse({'result': status})
  return JsonResponse({'result': 'error'})

# 파일 업로드 API
def upload(request):
  upload = core_mo.UPLOAD(
    file = request.FILES["file"]
  )
  upload.save()
  path = "/media/" + str(upload.file)
  return JsonResponse({
      "path": path # 파일 업로드 후 경로 반환
  })

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

# 회원 정보 조회 API(쪽지 발송 시 수신자 확인에 사용)
def search_user(request):
  id_or_nickname = request.GET.get('id_or_nickname', '')
  User = get_user_model()

  # 아이디 또는 닉네임으로 사용자 조회(일치 여부 확인)
  users = User.objects.filter(
    Q(username=id_or_nickname) | Q(first_name=id_or_nickname),
    status='active'
  )
  return JsonResponse({
    'result': 'success',
    'users': [{ # 사용자 정보 반환(list)
      'id': user.username,
      'nickname': user.first_name,
    } for user in users]
  })

# 쪽지 발송 API
def send_message(request):

  # 발신자 아이디 설정
  if not request.user.is_authenticated: # 비로그인 상태인 경우, 발신자를 guest로 설정
    guest_id = request.session['guest_id'] if 'guest_id' in request.session else None
    if not guest_id:
      guest_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    request.session['guest_id'] = guest_id
    sender_id = guest_id
  elif request.user.account_type == 'supervisor' or request.user.account_type == 'sub_supervisor': # 관리자 계정일 경우, 발신자를 supervisor로 설정
    sender_id = 'supervisor'
  else: # 그 외의 경우, 발신자를 로그인한 사용자로 설정
    sender_id = request.user.username

  # 쪽지 내용 설정
  receiver_id = request.POST.get('receiver_id', '') # 수신자 아이디
  title = request.POST.get('title', '') # 제목
  content = request.POST.get('content', '') # 내용
  include_coupon = request.POST.get('include_coupon', '') # 쿠폰 포함 여부(쿠폰은 쪽지를 통해 전달 가능)
  images = request.POST.get('images', '') # 이미지(이미지는 하나만 전달 가능)

  # 쪽지 저장
  message = message_mo.MESSAGE(
    sender_id = sender_id,
    receiver_id = receiver_id,
    title = title,
    content = content,
    include_coupon = include_coupon,
    images = images
  )
  message.save()

  # 쪽지 발송 활동기록 생성
  if request.user.is_authenticated: # 로그인 상태인 경우
    if request.user.account_type == 'user' or request.user.account_type == 'dame' or request.user.account_type == 'partner':

      # 관리자에게 보낸 경우, receiver를 'site_name'로 설정
      receiver = core_mo.SERVER_SETTING.objects.get(id='site_name').value
      if receiver_id != 'supervisor':
        rc = get_user_model().objects.get(username=receiver_id)
        receiver = rc.first_name

      activity = user_mo.ACTIVITY(
        message = f'[쪽지] {receiver}님에게 쪽지를 보냈습니다.',
        user_id = request.user.username,
      )
      activity.save()

  return JsonResponse({
    'result': 'success',
    'message_id': message.id
  })

# 사용자 정보 수정 API
def edit_user(request):
  User = get_user_model()

  if not request.user.is_authenticated: # 비로그인 상태인 경우, 에러 반환
    return JsonResponse({'result': 'error'})

  # 수정 대상 설정
  if request.user.account_type == 'supervisor' or request.user.account_type == 'sub_supervisor': # 관리자 계정일 경우, 수정 대상을 파라미터로 설정
    id = request.POST.get('id')
  else: # 그 외의 경우, 수정 대상을 로그인한 사용자로 설정
    id = request.user.username

  # 수정 대상 확인
  user = User.objects.get(username=id)

  # 정보 수정
  nickname = request.POST.get('nickname', user.first_name)
  user.first_name = nickname
  password = request.POST.get('password', '')
  if password != '':
    user.set_password(password)
  status = request.POST.get('status', user.status)
  user.status = status
  note = request.POST.get('note', user.note)
  user.note = note
  user_usable_point = request.POST.get('user_usable_point', user.user_usable_point)
  user.user_usable_point = user_usable_point
  user_level_point = request.POST.get('user_level_point', user.user_level_point)
  user.user_level_point = user_level_point
  user_level = request.POST.get('user_level', user.user_level)
  user.user_level = user_level
  partner_tel = request.POST.get('partner_tel', user.partner_tel)
  user.partner_tel = partner_tel
  partner_address = request.POST.get('partner_address', user.partner_address)
  user.partner_address = partner_address
  partner_categories = request.POST.get('partner_categories', user.partner_categories)
  user.partner_categories = partner_categories
  supervisor_permissions = request.POST.get('supervisor_permissions', user.supervisor_permissions)
  user.supervisor_permissions = supervisor_permissions

  # 저장
  user.save()

  # 활동 기록 생성
  if request.user.account_type == 'user' or request.user.account_type == 'dame' or request.user.account_type == 'partner': # 사용자 계정일 경우
    activity = user_mo.ACTIVITY(
      message = f'[계정] {nickname}님의 계정 정보를 수정했습니다.',
      user_id = request.user.username,
    )
    activity.save()
  else:
    activity = user_mo.ACTIVITY(
      message = f'[계정] 관리자에 의해 {nickname}님의 계정 정보가 수정되었습니다.',
      user_id = id
    )
    activity.save()

  return JsonResponse({'success': 'y'})

# 사용자 삭제 API
def delete_user(request):
  User = get_user_model()

  # 로그인 상태 확인
  if not request.user.is_authenticated: # 비로그인 상태인 경우, 에러 반환
    return JsonResponse({'result': 'error'})

  if request.user.account_type == 'supervisor' or request.user.account_type == 'sub_supervisor': # 관리자 계정일 경우, 삭제 대상을 파라미터로 설정
    id = request.POST.get('id')
  else: # 그 외의 경우, 삭제 대상을 로그인한 사용자로 설정
    id = request.user.username

  # 삭제 대상 확인
  user = User.objects.get(username=id)

  # 삭제
  user.is_active = False
  user.status = 'deleted'
  user.save()
  # 이후 last_login이 90일 이상 지나면 DB에서 삭제됨.(scheduler로 구현)

  # 활동 기록 생성
  if request.user.account_type == 'user' or request.user.account_type == 'dame' or request.user.account_type == 'partner': # 사용자 계정일 경우
    activity = user_mo.ACTIVITY(
      message = f'[계정] {user.first_name}님의 계정을 삭제했습니다.',
      user_id = request.user.username,
    )
    activity.save()
  else:
    activity = user_mo.ACTIVITY(
      message = f'[계정] 관리자에 의해 {user.first_name}님의 계정이 삭제되었습니다.',
      user_id = id
    )
    activity.save()

  return JsonResponse({'success': 'y'})

# 쿠폰 정보 조회 API
def search_coupon(request):

  # 쿠폰 코드로 쿠폰 조회
  coupon_code = request.GET.get('code', '')
  cp = coupon_mo.COUPON.objects.filter(
    code=coupon_code
  ).first()
  print(cp)

  if cp is None: # 쿠폰이 존재하지 않는 경우, not_exist 반환
    return JsonResponse({'result': 'not_exist', 'coupon_count': 0, 'coupon': {}})

  # 쿠폰 연관 게시글 조회
  # 각 쿠폰은 연관 게시글이 하나씩 존재함.
  pt = post_mo.POST.objects.filter(
    id=cp.post_id
  ).first()
  post = {
    'id': pt.id,
    'title': pt.title,
  }

  # 쿠폰 생성자 및 소유자 정보 확인
  # 쿠폰 생성자: 파트너 또는 관리자
  # 쿠폰 소유자: 사용자 또는 생성자
  oa = get_user_model().objects.filter(username=cp.own_user_id).first()
  own_account = {
    'id': oa.username,
    'nickname': oa.first_name,
  }
  ca = get_user_model().objects.filter(username=cp.create_account_id).first()
  create_account = {
    'id': ca.username,
    'nickname': ca.first_name,
  }

  # 쿠폰 정보 확인
  coupon = {
    'id': cp.id,
    'code': cp.code,
    'name': cp.name,
    'description': cp.description,
    'images': str(cp.images).split(','), #  각 쿠폰당 이미지는 하나씩만 등록됨.
    'post': post,
    'own_account': own_account,
    'create_account': create_account,
    'created_dt': cp.created_dt,
    'required_point': cp.required_point,
  }

  return JsonResponse({
    'result': 'success',
    'coupon_count': 1,
    'coupon': coupon
  })

# 댓글 작성 api
def write_comment(request):
  if request.method == 'POST':
    post_id = request.POST.get('post_id', '')
    comment_id = request.POST.get('comment_id', '')
    content = request.POST.get('content', '')

    if content == '': # 댓글 내용이 없는 경우
      return JsonResponse({'result': 'content_empty'})

    # 게시글 확인
    po = post_mo.POST.objects.filter(
      id=post_id
    ).first()
    if po is None: # 댓글을 작성할 게시긇이 없는 경우
      return JsonResponse({'result': 'post_not_exist'})

    # 게시판 확인
    bo = post_mo.BOARD.objects.filter(
      id=po.board_id
    ).first()
    # 게시글(게시판의 댓긓 작성 권한)에 댓글을 작성할 권한이 있는지 확인
    if request.user.account_type not in bo.comment_permissions:
      return JsonResponse({'result': 'permission_denied'})

    # 댓글 작성
    comment = post_mo.COMMENT(
      post_id=post_id,
      comment_id=comment_id,
      user_id=request.user.username,
      content=content
    )
    comment.save()

    # 댓글 작성 포인트 추가
    point = int(core_mo.SERVER_SETTING.objects.get(id='comment_point').value)
    request.user.user_usable_point += point
    request.user.user_level_point += point
    request.user.save()

    # 댓글 작성 활동기록 생성
    activity = user_mo.ACTIVITY(
      message = f'[게시판] {po.title} 게시글에 댓글을 작성했습니다.',
      user_id = request.user.username,
      point_change = '+' + point,
    )
    activity.save()

    return JsonResponse({'result': 'success'})

# 댓글 삭제 api
def delete_comment(request):
  if request.method == 'POST':
    comment_id = request.POST.get('comment_id', '')

    # 댓글 확인
    comment = post_mo.COMMENT.objects.filter(
      id=comment_id
    ).first()
    if comment is None: # 댓글이 존재하지 않는 경우
      return JsonResponse({'result': 'comment_not_exist'})

    # 권한 확인
    if comment.author_id  != request.user.username:
      # 관리자 또는 댓글 작성자만 삭제 가능
      if 'post' in request.user.supervisor_permissions:
        pass
      else:
        return JsonResponse({'result': 'permission_denied'})

    # 댓글 삭제
    comment.delete()

    return JsonResponse({'result': 'success'})

def read_message(request):
  message_id = request.GET.get('message_id', '')
  msg = message_mo.MESSAGE.objects.filter(
    id=message_id
  ).first()
  if msg:
    if not msg.read_dt:
      msg.read_dt = datetime.datetime.now()
      msg.save()

  return JsonResponse({'result': 'success'})

def receive_coupon(request):

  return JsonResponse({'result': 'success'})

def toggle_bookmark(request):
  # 게시글 아이디 확인
  post_id = request.GET.get('post_id', '')

  # 사용자 북마크 확인
  user_bookmarks = request.user.user_bookmarks.split(',')

  if post_id in user_bookmarks: # 북마크가 이미 존재하는 경우
    user_bookmarks.remove(post_id + ',') # 북마크 삭제
    message = 'remove'
  else: # 북마크가 존재하지 않는 경우
    user_bookmarks.append(post_id + ',') # 북마크 추가
    message = 'add'
  request.user.user_bookmarks = ','.join(user_bookmarks)
  request.user.save() # 북마크 저장

  return JsonResponse({'result': message})