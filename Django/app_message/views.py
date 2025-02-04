import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, get_user_model

from app_core import models
from app_core import daos

# 메세지 페이지
def index(request):
  # account, activities(5), unread_messages(5), coupons(5), server, best_reviews(5)
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  boards = daos.get_board_tree(contexts['account']['account_type']) # 게시판 정보

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
