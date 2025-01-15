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

# 파트너 카테고리 가져오기
# 파트너 카테고리는 트리 형태로, 최대 4단계까지 구성될 수 있음.
def get_categories():
  categories = partner_mo.CATEGORY.objects.all()
  category_dict = {
    category.name: {
      'id': category.id,
      'name': category.name,
      'children': [],
    } for category in categories if category.parent_id == ''
  }
  for category in categories:
    if category.parent_id:
      if category_dict.get(partner_mo.CATEGORY.objects.get(id=category.parent_id).name):
        category_dict[partner_mo.CATEGORY.objects.get(id=category.parent_id).name]['children'].append({
          'id': category.id,
          'name': category.name,
          'children': [],
        })
      else:
        loop = True
        for key in category_dict.keys():
          for child in category_dict[key]['children']:
            # 3단계 카테고리
            if not loop:
              break
            if str(child['id']) == str(category.parent_id):
              child['children'].append({
                'id': category.id,
                'name': category.name,
                'children': [],
              })
              loop = False
            # 4단계 카테고리
            if loop:
              for grandchild in child['children']:
                if not loop:
                  break
                if str(grandchild['id']) == str(category.parent_id):
                  grandchild['children'].append({
                    'id': category.id,
                    'name': category.name,
                    'children': [],
                  })
                  loop = False
  categories = []
  for child in category_dict.keys():
    categories.append(category_dict[child])

  return categories