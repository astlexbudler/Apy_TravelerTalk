import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, get_user_model
from django.conf import settings

from app_core import models
from app_core import daos

# 메세지 페이지
def index(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.make_board_tree() # 게시판 정보 가져오기

  # 리다이렉트
  if contexts['account']['account_type'] == 'guest': # 비회원인 경우
    return redirect('/?redirect_message=need_login') # 로그인 페이지로 리다이렉트
  if contexts['account']['account_type'] in ['supervisor', 'subsupervisor']:
    return redirect(settings.SUPERVISOR_URL + '/message')

  # 데이터 가져오기
  tab = request.GET.get('tab', 'inboxTab') # inbox 또는 outbox
  message_type = request.GET.get('message_type') # 메세지 타입
  page = int(request.GET.get('page', '1'))

  # 탭 확인
  if tab == 'inboxTab': # 받은 메세지함
    messages, last_page = daos.select_messages(receive_account_id=contexts['account']['id'], message_type=message_type, page=page)
  else: # 보낸 메세지함
    messages, last_page = daos.select_messages(send_account_id=contexts['account']['id'], message_type=message_type, page=page)

  return render(request, 'message/message.html', {
    **contexts,
    'boards': boards, # 게시판 정보

    'messages': messages, # 받은 메세지 또는 보낸 메세지 목록
    'last_page': last_page, # page 처리 작업에 사용(반드시 필요)
  })
