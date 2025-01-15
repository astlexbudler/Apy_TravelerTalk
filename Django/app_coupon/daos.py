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

# 현재 로그인한 사용자의 쿠폰 미리보기 정보 가져오기
# 사용자 계정은 계정이 현재 소유한 쿠폰을 가져옴.
# 파트너 계정은 파트너가 생성한 쿠폰의 정보를 가져옴
# 관리자 계정은 pass
def get_user_coupon_previews(request):
  coupon_preview = []

  # 로그인 및 계정 유효성 확인
  if request.user.is_authenticated:

    # 사용자는 본인이 소유한 쿠폰의 정보를 가져옴
    if request.user.account_type == 'user' or request.user.account_type == 'dame':

      # 사용자가 소율한 쿠폰 정보 가져오기
      cps = coupon_mo.COUPON.objects.filter(
        Q(own_user_id=request.user.username),
      ).order_by('-created_dt')[:5]

    # 파트너는 파트너가 생성한 쿠폰의 정보를 가져옴
    elif request.user.account_type == 'partner':

      # 파트너가 생성한 쿠폰 정보 가져오기
      cps = coupon_mo.COUPON.objects.filter(
        Q(create_account_id=request.user.username),
      ).order_by('-created_dt')[:5]

    else: # 관리자는 pass(guest 포함)
      return coupon_preview

    # 쿠폰 정보 확인
    for coupon in cps:

      # 쿠폰 여행지 정보 확인
      c_post = post_mo.POST.objects.filter(
        id=coupon.post_id,
      ).first()
      if not c_post:
        continue
      post = {
        'id': c_post.id,
        'title': c_post.title,
      }

      # 쿠폰 정보
      coupon_preview.append({
        'id': coupon.id,
        'name': coupon.name,
        'post': post,
        'created_dt': coupon.created_dt,
      })

  return coupon_preview











