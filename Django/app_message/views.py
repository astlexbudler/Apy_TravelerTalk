import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, get_user_model

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
# server, account, message, boards
def get_default_context(request):

  # 사용자 프로필 정보 가져오기
  # 로그인하지 않은 사용자는 guest로 처리
  account = user_do.get_user_profile(request)

  # 읽지 않는 쪽지 미리보기
  # 관리자의 경우 수신자가 'supervisor'인 쪽지로 검색해서 가져옴
  messages = message_do.get_user_message_previews(request)

  # 서버 설정 가져오기
  server = core_do.get_server_settings()

  # 게시판 트리 가져오기
  # 게시판 트리는 최대 4단계까지 구성됨.
  boards = post_do.get_boards()

  return {
    'server': server,
    'account': account,
    'messages': messages,
    'boards': boards,
  }

# 메세지 페이지
def index(request):
  context = get_default_context(request)

  # 메세지 전송(fetch)
  if request.method == 'POST':
    image = request.POST.get('image', '')
    receiver = request.POST.get('receiver', '') # 관리자일 경우 'supervisor' 그외 수신자 아이디(또는 게스트 아이디)
    title = request.POST.get('title', '')
    content = request.POST.get('content', '')
    coupon_code = request.POST.get('coupon_code', '') # 쿠폰이 담긴 경우 쿠폰 코드

    # 쿠폰 소유자 확인
    coupon = coupon_mo.COUPON.objects.filter(code=coupon_code).first()
    if coupon:
      # 1. 쿠폰 생성자인지 확인
      # 2. 이미 쿠폰을 다른 사용자에게 전달하지 않았는지 확인
      if coupon.create_account_id != context['account']['id'] or coupon.own_user_id != coupon.create_account_id:
        return JsonResponse({
          'success': 'n',
          'error': 'coupon_own_user_id',
        })

    # 메세지 저장
    message = message_mo.MESSAGE(
      sender_id=context['account']['id'],
      receiver_id=receiver,
      title=title,
      content=content,
      include_coupon=coupon_code,
      images=image,
    )
    message.save()

    # 활동 기록 저장
    if context['account']['account_type'] in ['user', 'dame', 'partner']:
      if receiver == 'supervisor':
        receiver = '관리자'
      act = user_mo.ACTIVITY(
        message = f'[메세지] {title} 메세지를 {receiver}님에게 전송하였습니다.',
        user_id = context['account']['id'],
        point_change = 0,
      )
      act.save()

    return JsonResponse({
      'success': 'y',
      'message_id': message.id,
    })

  # 메세지를 읽었을 때 처리(읽은 시간 업데이트 및 쿠폰 수신 처리)(fetch)
  if request.method == 'PATCH':
    message_id = request.GET.get('id')

    # 메세지 내 쿠폰 수신 처리
    coupon_code = request.GET.get('coupon_code')
    if coupon_code:
      acnt = get_user_model().objects.filter(username=context['account']['id']).first()
      coupon = coupon_mo.COUPON.objects.filter(code=coupon_code).first()
      if coupon: # 쿠폰 확인, 쿠폰 소유자 정보 업데이트
        coupon.own_user_id = acnt.username
        coupon.save()

      # 메세지 내 쿠폰 정보 업데이트
      message = message_mo.MESSAGE.objects.filter(id=message_id).first()
      message.include_coupon = ''
      message.save()

      # 활동 기록 저장
      act = user_mo.ACTIVITY(
        message = f'[쿠폰] {coupon.name} 쿠폰을 내 쿠폰함에 저장했습니다.',
        user_id = context['account']['id'],
        point_change = 0,
      )

      return JsonResponse({
        'success': 'y',
        'message': 'coupon_received',
      })

    # 메세지 읽음 처리
    message = message_mo.MESSAGE.objects.filter(id=message_id).first()
    # 메세지 수신자가 아직 읽지 않은 메세지를 읽은 경우
    if message.receiver_id == context['account']['id'] and message.read_dt == '':
      # 읽은 시간 업데이트
      message.read_dt = core_mo.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      message.save()

    return JsonResponse({
      'success': 'y',
      'message': 'message_read',
    })

  # data
  tab = request.GET.get('tab', 'inbox')
  page = int(request.GET.get('page', '1'))

  # 탭 확인
  if tab == 'inbox': # 받은 메세지함
    msgs = message_mo.MESSAGE.objects.filter(
      receiver_id=context['account']['id']
    ).order_by('-send_dt')
  else: # 보낸 메세지함
    msgs = message_mo.MESSAGE.objects.filter(
      sender_id=context['account']['id']
    ).order_by('-send_dt')
  print('account:', context['account']['id'])
  print(msgs)

  # 데이터 정리
  last_page = len(msgs) // 20 + 1 # 한 페이지당 20개씩 표시
  messages = []
  for msg in msgs[(page - 1) * 20:page * 20]:

    # 보낸 사람 정보
    sender = get_user_model().objects.filter(username=msg.sender_id).first()
    if sender:
      sender = {
        'id': sender.username,
        'nickname': sender.first_name,
        'account_type': sender.account_type,
      }
    else:
      sender = {
        'id':msg.sender_id,
        'nickname': 'guest',
        'account_type': 'guest',
      }

    # 받는 사람 정보
    receiver = get_user_model().objects.filter(username=msg.receiver_id).first()
    if receiver:
      receiver = {
        'id': receiver.username,
        'nickname': receiver.first_name,
        'account_type': receiver.account_type,
      }
    else:
      receiver = {
        'id': msg.receiver_id,
        'nickname': 'guest',
        'account_type': 'guest',
      }

    # 쿠폰 정보
    if msg.include_coupon:
      cu = coupon_mo.COUPON.objects.filter(code=msg.include_coupon).first()
      cu_post = post_mo.POST.objects.filter(id=cu.post_id).first()
      post = {
        'id': cu.post_id,
        'title': cu_post.title,
      }
      coupon = {
        'code': cu.code,
        'name': cu.name,
        'post': post,
        'own_user_id': cu.own_user_id,
        'create_account_id': cu.create_account_id,
        'required_point': cu.required_point,
      }
    else:
      coupon = None

    messages.append({
      'id': msg.id,
      'sender': sender,
      'receiver': receiver,
      'title': msg.title,
      'image': str(msg.images).split(',')[0],
      'content': msg.content,
      'send_dt': msg.send_dt,
      'read_dt': msg.read_dt,
      'include_coupon': coupon,
    })

  return render(request, 'message/index.html', {
    **context,
    'messages': messages, # 받은 메세지 또는 보낸 메세지 목록
    'last_page': last_page, # page 처리 작업에 사용(반드시 필요)
  })

# 사용 안함
'''
def write(request):
  if not request.user.is_authenticated:
    user_id = request.session.get('guest_id', ''.join(random.choices(string.ascii_letters + string.digits, k=16)))
    request.session['guest_id'] = user_id
  else:
    user_id = request.user.username

  if request.method == 'POST':
    receiver = request.POST.get('receiver')
    title = request.POST.get('title')
    content = request.POST.get('content')
    images = request.POST.get('images')
    include_coupon_id = request.POST.get('include_coupon_id')
    if include_coupon_id:
      include_coupon = coupon_mo.COUPON.objects.filter(id=include_coupon_id).first()
      if include_coupon.own_user_id != user_id:
        return JsonResponse({
          'success': 'n',
          'message': 'coupon_own_user_id'
        })
    message = message_mo.MESSAGE(
      sender_id=user_id,
      receiver_id=receiver,
      title=title,
      content=content,
      include_coupon=include_coupon,
      images=images,
    )
    message.save()
    return JsonResponse({
      'success': 'y',
    })

  context = get_default_context(request)
  return render(request, 'message/write.html', context)
'''

# 사용 안함
'''
def read(request):
  if not request.user.is_authenticated:
    user_id = request.session.get('guest_id', ''.join(random.choices(string.ascii_letters + string.digits, k=16)))
    request.session['guest_id'] = user_id
  else:
    user_id = request.user.username

  message_id = request.GET.get('id')
  message = message_mo.MESSAGE.objects.get(id=message_id)
  if message.receiver_id != user_id:
    if message.receiver_id != 'supervisor':
      return redirect('/message/')

  if message.read_dt == '':
    message.read_dt = core_mo.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message.save()

  context = get_default_context(request)
  return render(request, 'message/read.html', {
    **context,
    'message': {
      'id': message.id,
      'sender': {
        'nickname': get_user_model().objects.get(username=message.sender_id).first_name,
        'account_type': get_user_model().objects.get(username=message.sender_id).account_type,
      },
      'title': message.title,
      'content': message.content,
      'send_dt': message.send_dt,
      'read_dt': message.read_dt,
      'include_coupon': {
        'name': coupon_mo.COUPON.objects.get(code=message.include_coupon).name,
        'required_point': coupon_mo.COUPON.objects.get(code=message.include_coupon).required_point,
        'post': {
          'id': coupon_mo.COUPON.objects.get(code=message.include_coupon).post_id,
          'title': post_mo.POST.objects.get(id=coupon_mo.COUPON.objects.get(code=message.include_coupon).post_id).title,
        } if coupon_mo.COUPON.objects.get(code=message.include_coupon).post_id else None,
      } if message.include_coupon else None,
      'images': str(message.images).split(','),
    }
  })
'''
