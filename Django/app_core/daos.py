import datetime
import random
import string
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, logout, get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q, Count
from django.conf import settings
from . import models

# 기본 컨텍스트 정보 가져오기
def get_default_contexts(request):
  if request.user.is_authenticated: # 로그인 되어있는 경우
    # 사용자 정보 가져오기
    user = get_user_model().objects.select_related('level').prefetch_related('bookmarked_places').get(username=request.user.username)

    account = {
      'id': user.username,
      'nickname': user.first_name,
      'groups': [g.name for g in user.groups.all()],
      'status': user.status,
      'subsupervisor_permissions': str(user.subsupervisor_permissions).split(','),
      'mileage': user.mileage,
      'level': {
        'level': lv.level,
        'image': lv.image,
        'text': lv.text,
        'text_color': lv.text_color,
        'background_color': lv.background_color,
      } if (lv := user.level) else None, # 사용자 레벨 정보
      'bookmarked_places': [{
        'id': bp.id,
        'title': bp.title,
        'view_count': bp.view_count,
        'like_count': bp.like_count,
        'author': {
          'nickname': bp.author.last_name, # 작성자 파트너 이름
        },
        'place_info': {
          'categories': [c.name for c in pi.categories.all()],
        } if (pi := bp.place_info) else None,
      } for bp in user.bookmarked_places.all()[:5]],
    }

    # 사용자 활동 내역 가져오기
    activities = [{
      'id': a.id,
      'message': a.message,
      'mileage_change': a.mileage_change,
      'exp_change': a.exp_change,
      'created_at': a.created_at,
    } for a in models.ACTIVITY.objects.filter(account=request.user).order_by('-created_at')[:5]]

    # 받은 메세지 가져오기
    messages = [{
      'id': m.id,
      'title': m.title,
      'created_at': m.created_at,
    } for m in models.MESSAGE.objects.filter(to_account=request.user.username, is_read=False).order_by('-created_at')[:5]]

    # 내 쿠폰 가져오기
    cs = models.COUPON.objects.select_related('post').prefetch_related('own_accounts').filter(
      own_accounts=request.user, status='active'
    ).order_by('expire_at')[:5]
    coupons = [{
      'name': c.name,
      'expire_at': datetime.datetime.strftime(c.expire_at, '%Y-%m-%d'),
      'post': {
        'title': p.title,
      } if (p := c.post) else None,
    } for c in cs]

  else: # 로그인 되어있지 않은 경우
    guest_id = request.session.get('guest_id', ''.join(random.choices(string.ascii_letters + string.digits, k=16)))
    request.session['guest_id'] = guest_id
    account = {
      'id': guest_id,
    }
    activities = []
    messages = []
    coupons = []

  # 계정 타입 확인
  account_type = 'guest' # 기본값은 guest
  if request.user.is_authenticated:
    account_type = 'user'
    if 'admin' in account['groups']:
      account_type = 'admin'
    elif 'supervisor' in account['groups']:
      account_type = 'supervisor'
    elif 'subsupervisor' in account['groups']:
      account_type = 'subsupervisor'
    elif 'partner' in account['groups']:
      account_type = 'partner'
    elif 'dame' in account['groups']:
      account_type = 'dame'
  account['account_type'] = account_type

  # 서버 설정 확인
  server_settings = {
    'service_name': models.SERVER_SETTING.objects.get(name='service_name').value,
    'logo': models.SERVER_SETTING.objects.get(name='site_logo').value,
    'header_image': models.SERVER_SETTING.objects.get(name='site_header').value,
    'company_info': models.SERVER_SETTING.objects.get(name='company_info').value,
    'social_network': models.SERVER_SETTING.objects.get(name='social_network').value,
  }

  # 베스트 리뷰 5개
  review_board = models.BOARD.objects.filter(board_type='review').first()
  best_reviews = [{
    'id': r.id,
    'title': r.title,
    'view_count': r.view_count,
    'like_count': r.like_count,
    'author': {
      'nickname': r.author.first_name, # 작성자 닉네임
    },
  } for r in models.POST.objects.select_related('author').filter(boards=review_board).order_by('-search_weight')[:5]]

  return {
    'main_url': settings.MAIN_URL, # 메인 URL
    'partner_url': settings.PARTNER_URL, # 파트너 URL
    'supervisor_url': settings.SUPERVISOR_URL, # 관리자 URL

    'account': account, # 사용자 정보
    'activities': activities, # 사용자 활동 내역
    'unread_messages': messages, # 받은 메세지
    'coupons': coupons, # 내 쿠폰
    'server': server_settings, # 서버 설정
    'best_reviews': best_reviews, # 베스트 리뷰
  }

# 게시판 트리 가져오기
def get_board_tree(group_name):
  group = Group.objects.get(name=group_name)
  boards = models.BOARD.objects.filter(
    display_groups=group,
  ).order_by('-display_weight')
  board_dict = {
    board.name: {
      'id': board.id,
      'name': board.name,
      'board_type': board.board_type,
      'display': [g.name for g in board.display_groups.all()],
      'enter': [g.name for g in board.enter_groups.all()],
      'write': [g.name for g in board.write_groups.all()],
      'comment': [g.name for g in board.comment_groups.all()],
      'children': [],
    } for board in boards if not board.parent_board
  }
  for board in boards:
    if board.parent_board:
      if board_dict.get(board.parent_board.name):
        board_dict[board.parent_board.name]['children'].append({
          'id': board.id,
          'name': board.name,
          'board_type': board.board_type,
          'display': [g.name for g in board.display_groups.all()],
          'enter': [g.name for g in board.enter_groups.all()],
          'write': [g.name for g in board.write_groups.all()],
          'comment': [g.name for g in board.comment_groups.all()],
          'children': [],
        })
      else:
        loop = True
        for key in board_dict.keys():
          for child in board_dict[key]['children']:
            if not loop:
              break
            if str(child['name']) == str(board.parent_board.name):
              child['children'].append({
                'id': board.id,
                'name': board.name,
                'board_type': board.board_type,
                'display': [g.name for g in board.display_groups.all()],
                'enter': [g.name for g in board.enter_groups.all()],
                'write': [g.name for g in board.write_groups.all()],
                'comment': [g.name for g in board.comment_groups.all()],
                'children': [],
              })
              loop = False
            if loop:
              for grandchild in child['children']:
                if not loop:
                  break
                if str(grandchild['name']) == str(board.parent_board.name):
                  grandchild['children'].append({
                    'id': board.id,
                    'name': board.name,
                    'board_type': board.board_type,
                    'display': [g.name for g in board.display_groups.all],
                    'enter': [g.name for g in board.enter_groups.all()],
                    'write': [g.name for g in board.write_groups.all()],
                    'comment': [g.name for g in board.comment_groups.all()],
                    'children': [],
                  })
                  loop = False
  boards = []
  for child in board_dict.keys():
    boards.append(board_dict[child])
  return boards

# 여행지 게시판 가져오기
def get_travel_board_tree():
  def remove_empty_tree_nodes(data):
      def filter_nodes(nodes):
          return [
              node for node in nodes
              if not (node["board_type"] == "tree" and not node["children"])
          ]
      # 리스트를 필터링
      filtered_data = filter_nodes(data)
      # children 내부도 재귀적으로 검사
      for node in filtered_data:
          if "children" in node:
              node["children"] = filter_nodes(node["children"])
      return filtered_data

  boards = models.BOARD.objects.filter(
    Q(board_type='travel') | Q(board_type='tree') # 여행지 게시판 또는 트리
  ).order_by('-display_weight')
  board_dict = {
    board.name: {
      'id': board.id,
      'name': board.name,
      'board_type': board.board_type,
      'display': [g.name for g in board.display_groups.all()],
      'enter': [g.name for g in board.enter_groups.all()],
      'write': [g.name for g in board.write_groups.all()],
      'comment': [g.name for g in board.comment_groups.all()],
      'children': [],
    } for board in boards if not board.parent_board
  }
  for board in boards:
    if board.parent_board:
      if board_dict.get(board.parent_board.name):
        board_dict[board.parent_board.name]['children'].append({
          'id': board.id,
          'name': board.name,
          'board_type': board.board_type,
          'display': [g.name for g in board.display_groups.all()],
          'enter': [g.name for g in board.enter_groups.all()],
          'write': [g.name for g in board.write_groups.all()],
          'comment': [g.name for g in board.comment_groups.all()],
          'children': [],
        })
      else:
        loop = True
        for key in board_dict.keys():
          for child in board_dict[key]['children']:
            if not loop:
              break
            if str(child['name']) == str(board.parent_board.name):
              child['children'].append({
                'id': board.id,
                'name': board.name,
                'board_type': board.board_type,
                'display': [g.name for g in board.display_groups.all()],
                'enter': [g.name for g in board.enter_groups.all()],
                'write': [g.name for g in board.write_groups.all()],
                'comment': [g.name for g in board.comment_groups.all()],
                'children': [],
              })
              loop = False
            if loop:
              for grandchild in child['children']:
                if not loop:
                  break
                if str(grandchild['name']) == str(board.parent_board.name):
                  grandchild['children'].append({
                    'id': board.id,
                    'name': board.name,
                    'board_type': board.board_type,
                    'display': [g.name for g in board.display_groups.all],
                    'enter': [g.name for g in board.enter_groups.all()],
                    'write': [g.name for g in board.write_groups.all()],
                    'comment': [g.name for g in board.comment_groups.all()],
                    'children': [],
                  })
                  loop = False
  boards = []
  for child in board_dict.keys():
    boards.append(board_dict[child])
  boards = remove_empty_tree_nodes(boards)
  return boards

# 표시할 배너 정보 가져오기
def get_display_banners():
  banners = {
    'top': [], # 상단 배너
    'side': [], # 사이드 및 하단 배너
  }
  for b in models.BANNER.objects.all().order_by('-display_weight'):
    if b.location == 'top':
      banners['top'].append({
        'image': b.image,
        'link': b.link,
      })
    elif b.location == 'side':
      banners['side'].append({
        'image': b.image,
        'link': b.link,
      })
  return banners

# 카테고리 트리 가져오기
def get_category_tree():
  categories = models.CATEGORY.objects.select_related('parent_category').all().order_by('-display_weight')
  category_dict = {
    category.name: {
      'id': category.id,
      'name': category.name,
      'display_weight': category.display_weight,
      'children': [],
      'post_count': models.POST.objects.filter(place_info__categories=category).count(),
    } for category in categories if not category.parent_category
  }
  for category in categories:
    if category.parent_category:
      if category_dict.get(category.parent_category.name):
        category_dict[category.parent_category.name]['children'].append({
          'id': category.id,
          'name': category.name,
          'display_weight': category.display_weight,
          'children': [],
          'post_count': models.POST.objects.filter(place_info__categories=category).count(),
        })
      else:
        loop = True
        for key in category_dict.keys():
          for child in category_dict[key]['children']:
            if not loop:
              break
            if str(child['name']) == str(category.parent_category.name):
              child['children'].append({
                'id': category.id,
                'name': category.name,
                'display_weight': category.display_weight,
                'children': [],
                'post_count': models.POST.objects.filter(place_info__categories=category).count(),
              })
              loop = False
            if loop:
              for grandchild in child['children']:
                if not loop:
                  break
                if str(grandchild['name']) == str(category.parent_category.name):
                  grandchild['children'].append({
                    'id': category.id,
                    'name': category.name,
                    'display_weight': category.display_weight,
                    'children': [],
                    'post_count': models.POST.objects.filter(place_info__categories=category).count(),
                  })
                  loop = False
  categories = []
  for child in category_dict.keys():
    categories.append(category_dict[child])
  return categories

# 사용자 프로필 정보 가져오기
def get_user_profile_by_id(user_id):
  user = models.ACCOUNT.objects.select_related('level').prefetch_related('groups').filter(
    username=user_id
  ).first()
  user_info = {
    'id': user.username,
    'nickname': user.first_name,
    'partner_name': user.last_name,
    'email': user.email,
    'date_joined': user.date_joined,
    'last_login': user.last_login,
    'groups': [g.name for g in user.groups.all()],
    'status': user.status,
    'subsupervisor_permissions': user.subsupervisor_permissions,
    'level': {
      'level': lv.level,
      'image': lv.image,
      'text': lv.text,
      'text_color': lv.text_color,
      'background_color': lv.background_color,
    } if (lv := user.level) else None,
    'tel': user.tel,
    'exp': user.exp,
    'mileage': user.mileage,
    'note': user.note,
  }

  # 계정 타입 설정
  account_type = 'user'
  if 'admin' in user_info['groups']:
    account_type = 'admin'
  if 'supervisor' in user_info['groups']:
    account_type = 'supervisor'
  elif 'subsupervisor' in user_info['groups']:
    account_type = 'subsupervisor'
  elif 'partner' in user_info['groups']:
    account_type = 'partner'
  elif 'dame' in user_info['groups']:
    account_type = 'dame'
  user_info['account_type'] = account_type

  return user_info

# 레벨 규칙 정보 가져오기
def get_all_level_rules():
  rules = models.LEVEL_RULE.objects.all().order_by('level')
  return [{
    'level': rule.level,
    'image': rule.image,
    'text': rule.text,
    'text_color': rule.text_color,
    'background_color': rule.background_color,
    'required_exp': rule.required_exp,
  } for rule in rules]

# 사용자 활동 내역 가져오기
def get_user_activities(user_id, page):
  user_id = models.ACCOUNT.objects.get(username=user_id).id
  acts = models.ACTIVITY.objects.filter(account=user_id).order_by('-created_at')
  last_page = len(acts) // 20 + 1
  activities = [{
    'id': a.id,
    'message': a.message,
    'exp_change': a.exp_change,
    'mileage_change': a.mileage_change,
    'created_at': a.created_at,
  } for a in acts[(page - 1) * 20:page * 20]]
  return activities, last_page

# 사용자의 모든 북마크 가져오기
def get_all_bookmarked_places(user_id):
  bookmarks = models.ACCOUNT.objects.prefetch_related('bookmarked_places').prefetch_related('bookmarked_places__place_info__categories',).get(
    username=user_id
  ).bookmarked_places.all()
  return [{
    'id': b.id,
    'title': b.title,
    'image': '/media/' + str(b.image) if b.image else '/media/default.png',
    'place_info': {
      'categories': [c.name for c in b.place_info.categories.all()],
      'address': b.place_info.address,
      'location_info': b.place_info.location_info,
      'open_info': b.place_info.open_info,
      'status': b.place_info.status,
    },
  } for b in bookmarks]

# 사용자의 모든 쿠폰 가져오기
def get_all_user_coupons(user_id, page):
  coupons = models.COUPON.objects.select_related('post', 'create_account').prefetch_related('own_accounts').filter(
    own_accounts__username=user_id,
    status='active',
  ).order_by('expire_at')
  print(coupons)
  last_page = len(coupons) // 20 + 1
  coupons = [{
    'code': c.code,
    'name': c.name,
    'image': '/media/' + str(c.image) if c.image else None,
    'content': c.content,
    'required_mileage': c.required_mileage,
    'expire_at': datetime.datetime.strftime(c.expire_at, '%Y-%m-%d'),
    'status': c.status,
    'post': {
      'id': c.post.id,
      'title': c.post.title,
    },
    'create_account': {
      'partner_name': c.create_account.last_name,
    },
  } for c in coupons[(page - 1) * 20:page * 20]]
  return coupons, last_page

# 사용자의 사용된 쿠폰 내역 가져오기
def get_all_coupon_histories(user_id, page):
  coupons = models.COUPON.objects.select_related('post', 'create_account').prefetch_related('used_account').exclude(
    status='active',
  ).filter(
    used_account__username=user_id,
  )
  last_page = len(coupons) // 20 + 1
  coupons = [{
    'code': c.code,
    'name': c.name,
    'image': '/media/' + str(c.image) if c.image else None,
    'content': c.content,
    'required_mileage': c.required_mileage,
    'expire_at': c.expire_at,
    'status': c.status,
    'post': {
      'id': c.post.id,
      'title': c.post.title,
    },
    'create_account': {
      'partner_name': c.create_account.last_name,
    },
  } for c in coupons[(page - 1) * 20:page * 20]]
  return coupons, last_page

# 사용자가 받은 메세지 가져오기
def get_user_inbox_messages(user_id, page):
  msgs = models.MESSAGE.objects.select_related('include_coupon').filter(to_account=user_id)
  msgs = msgs.order_by('-created_at')
  last_page = len(msgs) // 20 + 1
  messages = [{
    'id': m.id,
    'title': m.title,
    'content': m.content,
    'is_read': m.is_read,
    'created_at': m.created_at,
    'image': str(m.image),
    'include_coupon': {
      'code': m.include_coupon.code,
      'name': m.include_coupon.name,
    } if m.include_coupon else None,
    'sender': {
      'id': sd.username,
      'nickname': sd.first_name,
      'partner_name': sd.last_name,
      'level': {
        'level': sd.level.level,
        'image': sd.level.image,
        'text': sd.level.text,
        'text_color': sd.level.text_color,
        'background_color': sd.level.background_color,
      } if sd.level else None,
      'groups': [g.name for g in sd.groups.all()],
    } if (sd := get_user_model().objects.prefetch_related('groups').select_related('level').get(username=m.sender_account)) else {'id': m.sender_account},
  } for m in msgs[(page - 1) * 20:page * 20]]
  return messages, last_page

# 사용자가 보낸 메세지 가져오기
def get_user_outbox_messages(user_id, page):
  msgs = models.MESSAGE.objects.select_related('include_coupon').filter(sender_account=user_id)
  msgs = msgs.order_by('-created_at')
  last_page = len(msgs) // 20 + 1
  messages = [{
    'id': m.id,
    'title': m.title,
    'content': m.content,
    'is_read': m.is_read,
    'created_at': m.created_at,
    'image': str(m.image),
    'include_coupon': {
      'code': m.include_coupon.code,
      'name': m.include_coupon.name,
    } if m.include_coupon else None,
    'to': {
      'id': rc.username,
      'nickname': rc.first_name,
      'partner_name': rc.last_name,
      'level': {
        'level': rc.level.level,
        'image': rc.level.image,
        'text': rc.level.text,
        'text_color': rc.level.text_color,
        'background_color': rc.level.background_color,
      } if rc.level else None,
      'groups': [g.name for g in rc.groups.all()],
    } if (rc := get_user_model().objects.prefetch_related('groups').select_related('level').get(username=m.to_account)) else {'id': m.to_account},
  } for m in msgs[(page - 1) * 20:page * 20]]
  return messages, last_page

# 파트너가 작성한 여행지 게시글 가져오기
def get_partner_place_post(partner_id):
  post = models.POST.objects.select_related('place_info', 'author').prefetch_related('place_info__categories').filter(
    author=partner_id
  ).first()
  return {
    'id': post.id,
    'title': post.title,
    'image_paths': post.image_paths,
    'content': post.content,
    'view_count': post.view_count,
    'like_count': post.like_count,
    'search_weight': post.search_weight,
    'created_at': post.created_at,
    'author': {
      'nickname': post.author.first_name,
      'partner_name': post.author.last_name,
    },
    'place_info': {
      'categories': [c.name for c in post.place_info.categories.all()],
      'address': post.place_info.address,
      'location_info': post.place_info.location_info,
      'open_info': post.place_info.open_info,
      'ad_start_at': post.place_info.ad_start_at,
      'ad_end_at': post.place_info.ad_end_at,
      'status': post.place_info.status
    },
  } if post else None

# 선택된 게시판 정보 가져오기
def get_selected_board_info(board_ids):
  boards = models.BOARD.objects.filter(id__in=board_ids)
  return [{
    'id': b.id,
    'name': b.name,
    'board_type': b.board_type,
    'display': [g.name for g in b.display_groups.all()],
    'enter': [g.name for g in b.enter_groups.all()],
    'write': [g.name for g in b.write_groups.all()],
    'comment': [g.name for g in b.comment_groups.all()],
  } for b in boards]


# 선택된 게시판의 게시글 가져오기
def get_board_posts(board_ids, page, search):

  posts = models.POST.objects.select_related(
      'author', 'place_info', 'review_post'
  ).prefetch_related('place_info__categories', 'review_post__place_info').filter(
      title__contains=search
  ).annotate( # 게시글이 포함된 게시판 수
      board_count=Count('boards', filter=Q(boards__id__in=board_ids), distinct=True)
  ).filter( # 게시글이 포함된 게시판 수가 전체 게시판 수와 같은 게시글만 필터
      board_count=len(board_ids)  # 모든 board_ids 포함된 게시글만 필터
  ).order_by('search_weight', '-created_at')
  last_page = len(posts) // 20 + 1
  posts = [{
    'id': p.id,
    'title': p.title,
    'image': '/media/' + str(p.image) if p.image else '/media/default.png',
    'view_count': p.view_count,
    'like_count': p.like_count,
    'created_at': p.created_at,
    'author': {
      'nickname': p.author.first_name, # 작성자 닉네임
      'partner_name': p.author.last_name, # 작성자 파트너 이름
    },
    'place_info': { # 여행지 게시글인 경우, 여행지 정보
      'categories': [c.name for c in p.place_info.categories.all()],
      'address': p.place_info.address,
      'location_info': p.place_info.location_info,
      'open_info': p.place_info.open_info,
      'status': p.place_info.status,
    } if p.place_info else None,
    'review_post': { # 리뷰 게시글인 경우, 리뷰 대상 게시글 정보
      'id': p.review_post.id,
      'title': p.review_post.title,
    } if p.review_post else None,
  } for p in posts[(page - 1) * 20:page * 20]]
  return posts, last_page

# 게시글 내용 가져오기
def get_post_info(post_id):
  post = models.POST.objects.prefetch_related('boards').select_related(
    'author', 'place_info', 'review_post'
  ).prefetch_related('place_info__categories', 'review_post__place_info',).get(id=post_id)
  return {
    'id': post.id,
    'boards': [{
      'id': b.id,
      'name': b.name,
      'comment': [g.name for g in b.comment_groups.all()],
      'level_cut': b.level_cut,
      'board_type': b.board_type,
    } for b in post.boards.all()],
    'board_ids': [b.id for b in post.boards.all()],
    'title': post.title,
    'image': '/media/' + str(post.image) if post.image else '/media/default.png',
    'content': post.content,
    'view_count': post.view_count,
    'like_count': post.like_count,
    'created_at': post.created_at,
    'author': {
      'id': post.author.username,
      'nickname': post.author.first_name,
      'partner_name': post.author.last_name,
    },
    'place_info': {
      'categories': [c.name for c in post.place_info.categories.all()],
      'category_ids': [c.id for c in post.place_info.categories.all()],
      'address': post.place_info.address,
      'location_info': post.place_info.location_info,
      'open_info': post.place_info.open_info,
      'status': post.place_info.status,
    } if post.place_info else None,
    'review_post': {
      'id': post.review_post.id,
      'title': post.review_post.title,
    } if post.review_post else None,
  }

# 게시글 댓글 가져오기
def get_all_post_comments(post_id):
  cs = models.COMMENT.objects.select_related('author').select_related('author__level').filter(post=post_id).order_by('-created_at')
  comments = [{
    'id': c.id,
    'content': c.content,
    'created_at': c.created_at,
    'author': {
      'id': c.author.username,
      'nickname': c.author.first_name,
      'partner_name': c.author.last_name,
      'level': {
        'level': c.author.level.level,
        'image': c.author.level.image,
        'text': c.author.level.text,
        'text_color': c.author.level.text_color,
        'background_color': c.author.level.background_color,
      } if c.author.level else None,
    },
  } for c in cs]
  return comments

# 레벨업 확인
def check_level_up(user_id):
  user = models.ACCOUNT.objects.select_related('level').get(username=user_id)
  level_rules = models.LEVEL_RULE.objects.all().order_by('level')

  # 레벨업 조건 확인
  for rule in level_rules:
    if user.exp >= rule.required_exp: # 레벨업 조건 충족
      if not user.level or user.level.level < rule.level:
        user.level = rule # 레벨업
        user.save()