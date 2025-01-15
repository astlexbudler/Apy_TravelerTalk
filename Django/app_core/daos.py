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

# 사용자의 레벨 정보를 가져오기
# 사용자가 잘못 되어있는 경우, 레벨 0 정보 반환
def get_user_level(user):
  if user.is_authenticated:
    user_lv = core_mo.LEVEL_RULE.objects.filter(level=user.user_level).first()
    if user_lv:
      return {
        'level': user_lv.level,
        'name': user_lv.name,
        'background_color': user_lv.background_color,
        'text_color': user_lv.text_color,
      }
  return {
    'level': 0,
    'name': '',
    'background_color': '#ffffff',
    'text_color': '#000000',
  }

# 기본 서버 설정 정보 가져오기
def get_server_settings():
  return {
    'title': core_mo.SERVER_SETTING.objects.get(id='site_name').value,
    'logo': core_mo.SERVER_SETTING.objects.get(id='site_logo').value,
    'favicon': core_mo.SERVER_SETTING.objects.get(id='site_favicon').value,
    'company': core_mo.SERVER_SETTING.objects.get(id='company_name').value,
    'tel': core_mo.SERVER_SETTING.objects.get(id='company_tel').value,
    'email': core_mo.SERVER_SETTING.objects.get(id='company_email').value,
    'address': core_mo.SERVER_SETTING.objects.get(id='company_address').value,
    'x_link': core_mo.SERVER_SETTING.objects.get(id='social_network_x').value,
    'meta_link': core_mo.SERVER_SETTING.objects.get(id='social_network_meta').value,
    'instagram_link': core_mo.SERVER_SETTING.objects.get(id='social_network_instagram').value,
    }

# 서버에 설정된 레벨 규칙 가져오기
def get_level_rules():
  lvrs = core_mo.LEVEL_RULE.objects.all()
  level_rules = []
  for lv in lvrs:
    level_rules.append({
      'level': lv.level,
      'text_color': lv.text_color,
      'background_color': lv.background_color,
      'name': lv.name,
      'required_point': lv.required_point,
    })
  return level_rules