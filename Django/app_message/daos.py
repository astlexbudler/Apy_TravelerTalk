import datetime
import random
import string
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, logout, get_user_model
from django.db.models import Q

from app_core import models as core_mo
from app_user import models as user_mo
from app_partner import models as partner_mo
from app_supervisor import models as supervisor_mo
from app_post import models as post_mo
from app_message import models as message_mo
from app_coupon import models as coupon_mo

from app_core import daos as core_do
from app_user import daos as user_do
from app_post import daos as post_do

# 사용자 계정의 메세지 미리보기 가져오기
# 메세지 미리보기는 최신 5개의 읽지 않은 메세지만 가져옴.
# 이미지 또는 쿠폰이 메세지에 포함되는지 여부만 확인함.(is_include_image, is_include_coupon)
def get_user_message_previews(request):
  message_preview = []

  # 로그인 및 계정 유효성 확인
  if request.user.is_authenticated:

    # 관리자 메세제의 경우, 따로 처리
    if 'supervisor' in request.user.account_type:

      # 관리자가 받은 메세지는 모두 receiver_id가 'supervisor'로 저장됨.
      # 관리자 메세지는 다른 관리자들과 서로 공유됨.
      msgs = message_mo.MESSAGE.objects.filter(
        Q(receiver_id='supervisor'), # 관리자 메세지
      ).order_by('-send_dt')[:5]

    # 사용자 메세지 가져오기
    else:

      # 받은 메세지 중 읽지 않은 메세지 5개 가져오기(최신순)
      msgs = message_mo.MESSAGE.objects.filter(
        Q(receiver_id=request.user.username),
        read_dt=None
      ).order_by('-send_dt')[:5]

    # 메세지 정보 확인
    for message in msgs:

      # 메세지 발송자 정보 확인(sender)
      # 발송자가 존재하지 않는 경우, 게스트로 처리
      sd = get_user_model().objects.filter(
        username=message.sender_id,
      ).first()
      if not sd:
        sender = {
          'id': message.sender_id,
          'nickname': '게스트',
          'account_type': 'guest',
          'status': 'active',
        }
      else:
        if sd.account_type in ['user', 'dame']:
          lv = core_mo.LEVEL_RULE.objects.filter(
            level=sd.user_level
          ).first()
          level = {
            'level': lv.level,
            'name': lv.name,
            'background_color': lv.background_color,
            'text_color': lv.text_color,
          }
        else:
          level = None

        sender = {
          'id': request.user.username,
          'nickname': request.user.first_name,
          'account_type': request.user.account_type,
          'status': request.user.status,
          'level': level,
        }

      # 메세지 정보 저장
      message_preview.append({
        'id': message.id,
        'title': message.title,
        'sender': sender,
        'send_dt': message.send_dt,
        'is_include_image': True if message.images else False,
        'is_include_coupon': True if message.include_coupon else False,
      })

  return message_preview