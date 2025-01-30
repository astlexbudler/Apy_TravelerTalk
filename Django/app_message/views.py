import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, get_user_model

from app_core import models
from app_core import daos

# 메세지 페이지
def index(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree() # 게시판 정보 가져오기

  '''
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
  '''

  # 데이터 가져오기
  tab = request.GET.get('tab', 'inbox') # inbox 또는 outbox
  page = int(request.GET.get('page', '1'))

  # 탭 확인
  if tab == 'inbox': # 받은 메세지함
    messages, last_page = daos.get_user_inbox_messages(contexts['account']['id'], page)
  elif tab == 'outbox': # 보낸 메세지함
    messages, last_page = daos.get_user_outbox_messages(contexts['account']['id'], page)

  return render(request, 'message/index.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'messages': messages, # 받은 메세지 또는 보낸 메세지 목록
    'last_page': last_page, # page 처리 작업에 사용(반드시 필요)
  })
