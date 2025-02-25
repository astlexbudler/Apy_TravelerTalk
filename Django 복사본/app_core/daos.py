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

####################
# DAOS
# * 아래 dao 함수들에 대해서는 권한을 확인할 필요는 없음. 권한 확인은 views에서 처리
# * page 파라메터를 받는 함수들은 반환 시 last_page도 함께 반환(페이지네이션을 위함) 예: return activities, last_page
# get_default_contexts(request): 기본 컨텍스트 정보 가져오기
#  - account, activities_preview, unread_messages, coupons_preview, best_reviews, server_settings
#  - 각 항목은 사용자 정보, 사용자 활동 내역, 받은 메세지, 내 쿠폰, 베스트 리뷰, 서버 설정 정보로 구성. 다른 함수를 통해 각 항목을 가져옴
##### [ACCOUNT]
# select_account(account_id): 사용자 정보 가져오기
#  - username(로그인 아이디), nickname(first_name 닉네임), partner_name(last_name 파트너 이름), email, group(그룹), status(상태), subsupervisor_permissions(부관리자 권한), level(레벨), exp(경험치), mileage(마일리지)
#  - level은 레벨 정보를 가져오며, 레벨 정보는 level(레벨), image(레벨 이미지), text(레벨 텍스트), text_color(텍스트 색상), background_color(배경 색상)로 구성됨.
# select_account_detail(account_id): 사용자 상세 정보 가져오기(모든 정보)
#  - select_account를 통해 가져온 정보에 추가로 note(메모)도 포함해서 반환하도록 함
# create_account(data): 사용자 생성
#  - id, password, nickname, partner_name, email, group, account_type를 받아 사용자 생성
#  - exp, mileage는 SERVER_SETTING.register_point에 설정된 값으로 초기화. level은 1로 초기화
#  - 만약 account_type이 partner, dame인 경우 staus를 'pending'으로 설정. 그 외 경우 'active'로 설정. account_type과 같은 이름의 GROUP을 ACCOUNT에 할당(user, dame, partner, subsupervisor)
# update_account(account_id, data): 사용자 정보 업데이트
#  - data에 포함되어있는 정보만 업데이트, password는 set_password로 업데이트
#  - password, nickname(first_name 닉네임), partner_name(last_name 파트너 이름), email, status, note, subsupervisor_permissions, exp, mileage를 업데이트
# delete_account(account_id): 사용자 삭제(모든 정보 삭제)
#  - 사용자 정보 삭제. 사용자를 삭제하면 나머지 정보는 cascade로 삭제됨.
#  - 이 함수는 시스템에 의해서 자동으로 사용자를 삭제하는 경우에만 사용됨. 사용자가 직접 삭제하면 30일 후 삭제되도록 설정됨.(schedule로 처리)
# search_accounts(nickname=None, id=None, any=None): 사용자 검색(닉네임, 아이디, 모두)
#  - nickname(first_name 닉네임), id(username 로그인 아이디)로 검색. any(닉네임 또는 아이디)로 검색
#  - username, nickname, status 반환
##### [ACTIVITY]
# get_account_activity_stats(account_id, page=1): 사용자 활동 통계 정보 가져오기
#  - message(활동 내용), exp_change(경험치 변화), mileage_change(마일리지 변화), created_at(생성일)로 구성
#  - 사용자의 활동 내역을 가져오며, page에 따라 20개씩 가져옴
# select_account_activities(account_id, page): 사용자 활동 내역 가져오기
#  - 사용자의 활동 내역을 가져오며, page에 따라 20개씩 가져옴
#  - id, message, exp_change, mileage_change, created_at 반환
# create_account_activity(account_id, data): 사용자 활동 생성
#  - message(활동 내용), exp_change(경험치 변화), mileage_change(마일리지 변화)를 받아 사용자 활동 생성
##### [LEVEL]
# select_level(level): 레벨 정보 가져오기
#  - level(레벨), image(레벨 이미지), text(레벨 텍스트), text_color(텍스트 색상), background_color(배경 색상)로 구성
# select_all_levels(): 모든 레벨 정보 가져오기
#  - 모든 레벨 정보를 가져오며, level, image, text, text_color, background_color로 구성
# create_level(data): 레벨 생성
#  - level(레벨), image(레벨 이미지), text(레벨 텍스트), text_color(텍스트 색상), background_color(배경 색상)를 받아 레벨 생성
# update_level(level, data): 레벨 정보 업데이트
#  - data에 포함되어있는 정보만 업데이트. level은 변경 불가
##### [POST & PLACE_INFO]
# search_posts(title=None, category_id=None, board_id=None, page=1): 게시글 검색(제목, 카테고리, 게시판, 페이지)
#  - title(제목), category(카테고리), board(게시판)로 검색. page에 따라 20개씩 가져옴
#  - POST.boards에 포함된 게시판 검색 boards__id__in, category_id는 PLACE_INFO.categories__id__in으로 검색
#  - id, author(작성자), related_post(관련 게시글), place_info(여행지 정보), boards(게시판), title(제목), content(내용 toastfulEditor), image(대표 이미지), view_count(조회수), like_count(좋아요수), created_at(생성일), comment_count(댓글수) 반환
#  - search_weight 내림차순 정렬 및 created_at 내림차순 정렬
#  - author는 nickname(first_name 닉네임), partner_name(last_name 파트너 이름), level(level, image, text, text_color, background_color)로 구성
#  - place_info는 categories(id, name), location_info, open_info, status로 구성
#  - related_post는 id, title로 구성
#  - boards는 id, name로 구성
# select_post(post_id): 게시글 정보 가져오기
#  - id, author(작성자), related_post(관련 게시글), place_info(여행지 정보), boards(게시판), title(제목), content(내용 toastfulEditor), view_count(조회수), like_count(좋아요수), created_at(생성일) 반환.
# create_post(data): 게시글 생성
#  - author(작성자), related_post_id(관련 게시글), title(제목), content(내용 toastfulEditor), image(대표 이미지), board_ids(게시판)를 받아 게시글 생성
#  - 생성된 게시글의 id 반환
# create_post_place_info(data): 게시글의 여행지 정보 생성
#  - post_id(게시글), category_ids(카테고리), location_info(위치 정보), open_info(영업 정보), status(상태)를 받아 여행지 정보 생성
# update_post(post_id, data): 게시글 정보 업데이트
#  - data에 포함되어있는 정보만 업데이트
#  - title(제목), content(내용 toastfulEditor), image(대표 이미지), board_ids(게시판)를 받아 게시글 정보 업데이트
#  - 변경한 게시글의 id 반환
# update_place_info(post_id, data): 게시글의 여행지 정보 업데이트
#  - data에 포함되어있는 정보만 업데이트
#  - category_ids(카테고리), location_info(위치 정보), open_info(영업 정보), status(상태)를 받아 여행지 정보 업데이트
#  - 변경한 게시글의 id 반환
# increase_post_like(post_id, account_id): 게시글 좋아요 추가
#  - 게시글 좋아요 추가. 게시글 좋아요 추가 시 ACCOUNT.like_posts에 추가
#  - 게시글의 like_count 증가
# decrease_post_like(post_id, account_id): 게시글 좋아요 삭제
#  - 게시글 좋아요 삭제. 게시글 좋아요 삭제 시 ACCOUNT.like_posts에서 삭제
#  - 게시글의 like_count 감소
# increase_post_view(post_id): 게시글 조회수 증가
#  - 게시글 조회수 증가
# delete_post(post_id): 게시글 삭제
#  - 게시글 삭제. 게시글을 삭제하면 나머지 정보는 cascade로 삭제됨.
##### [COMMENT]
# select_comments(post_id): 게시글 댓글 가져오기
#  - post_id에 해당하는 게시글의 댓글을 가져옴
#  - id, account(작성자), content(내용), created_at(생성일) 반환
#  - account는 nickname(first_name 닉네임), partner_name(last_name 파트너 이름), level(level, image, text, text_color, background_color)로 구성
# create_comment(data): 댓글 생성
#  - post_id(게시글), account_id(작성자), content(내용)을 받아 댓글 생성
# update_comment(comment_id, data): 댓글 업데이트
#  - data에 포함되어있는 정보만 업데이트
#  - content(내용)을 받아 댓글 업데이트
# delete_comment(comment_id): 댓글 삭제
#  - 댓글 삭제
##### [COUPON]
# select_all_coupons(status=None): 모든 쿠폰 정보 가져오기
#  - status에 따라 쿠폰 정보를 가져옴.
#  - status가 없는 경우, 모든 쿠폰. not_active인 경우, active가 아닌 모든 쿠폰. 그 외 status가 status인 쿠폰을 가져옴
#  - code, related_post(관련 게시글), name(이름), content(toastfulEditor), image(이미지), expire_at(만료일), required_mileage(필요 마일리지), own_accounts(소유 계정), status(상태) 반환
#  - related_post는 id, title로 구성, own_accounts는 id, nickname로 구성
# select_created_coupons(account_id, status=None): 사용자가 생성한 쿠폰 정보 가져오기
#  - create_account__id=account_id이며 status에 따라 쿠폰 정보를 가져옴.
#  - status가 없는 경우, 모든 쿠폰. not_active인 경우, active가 아닌 모든 쿠폰. 그 외 status가 status인 쿠폰을 가져옴
#  - code, related_post(관련 게시글), name(이름), content(toastfulEditor), image(이미지), expire_at(만료일), required_mileage(필요 마일리지), own_accounts(소유 계정), status(상태) 반환
# select_owned_coupons(account_id, status=None): 사용자가 소유한 쿠폰 정보 가져오기
#  - own_accounts__id=account_id이며 status에 따라 쿠폰 정보를 가져옴.
#  - status가 없는 경우, 모든 쿠폰. not_active인 경우, active가 아닌 모든 쿠폰. 그 외 status가 status인 쿠폰을 가져옴
#  - code, related_post(관련 게시글), name(이름), content(toastfulEditor), image(이미지), expire_at(만료일), required_mileage(필요 마일리지), own_accounts(소유 계정), status(상태) 반환
# create_coupon(data): 쿠폰 생성
#  - code, related_post_id(관련 게시글), name(이름), content(toastfulEditor), image(이미지), expire_at(만료일), required_mileage(필요 마일리지)를 받아 쿠폰 생성
# update_coupon(coupon_id, data): 쿠폰 정보 업데이트
#  - data에 포함되어있는 정보만 업데이트
#  - name(이름), content(toastfulEditor), image(이미지), expire_at(만료일), required_mileage(필요 마일리지), own_account_id(소유 계정), status(상태)를 받아 쿠폰 정보 업데이트
##### [MESSAGE]
# select_received_messages(account_id, page=1): 사용자가 받은 메세지 가져오기
#  - to_account=account_id인 메세지를 가져옴
#  - title(제목), sender(보낸 사람), content(내용), created_at(생성일), is_read(읽음 여부), include_coupon(쿠폰)
#  - sender는 id, nickname로 구성
#  - sender_id가 supervisor인 경우, nickname로 '관리자'로 표시. 그 외 ACCOUNT.username이 sender_id인 사용자의 first_name으로 표시. 만약 ACCOUNT가 존재하지 않는 경우, nickname로 '게스트'으로 표시
#  - include_coupon은 code, name, related_post(title)로 구성
#  - page에 따라 20개씩 가져옴
# select_sent_messages(account_id): 사용자가 보낸 메세지 가져오기
#  - from_account=account_id인 메세지를 가져옴
#  - title(제목), receiver(받는 사람), content(내용), created_at(생성일), is_read(읽음 여부), include_coupon(쿠폰)
#  - receiver는 id, nickname로 구성. receiver_id가 supervisor인 경우, nickname로 '관리자'로 표시. 그 외 ACCOUNT.username이 receiver_id인 사용자의 first_name으로 표시. 만약 ACCOUNT가 존재하지 않는 경우, nickname로 '게스트'으로 표시
#  - include_coupon은 code, name, related_post(title)로 구성
#  - page에 따라 20개씩 가져옴
# create_message(data): 메세지 생성
#  - sender, receiver, title, content, image, include_coupon_code를 받아 메세지 생성
# update_message(message_id, data): 메세지 정보 업데이트
#  - data에 포함되어있는 정보만 업데이트
#  - title(제목), content(내용), image(이미지), is_read(읽음 여부)를 받아 메세지 정보 업데이트
##### [SERVER_SETTING & UPLOAD]
# select_all_server_settings(): 모든 서버 설정 가져오기
#  - name, value로 구성
#  - 각 name을 key로 하는 dict 형태로 반환
# select_server_setting(name): 서버 설정 가져오기
#  - name에 해당하는 서버 설정 가져오기
#  - value 반환
# update_server_setting(name, value): 서버 설정 업데이트
#  - value를 업데이트
# upload_file(file): 파일 업로드 및 경로 반환
#  - 파일을 업로드하고 업로드된 파일의 URL을 반환(UPLOAD)
##### [BANNER]
# select_banners(): 배너 정보 가져오기
#  - id, image(이미지), link(링크), display_weight(가중치), location(위치)로 구성
# create_banner(data): 배너 생성
#  - image(이미지), link(링크), display_weight(가중치), location(위치)를 받아 배너 생성
# update_banner(banner_id, data): 배너 정보 업데이트
#  - data에 포함되어있는 정보만 업데이트
#  - image(이미지), link(링크), display_weight(가중치), location(위치)를 받아 배너 정보 업데이트
# delete_banner(banner_id): 배너 삭제
#  - 배너 삭제
##### [STATISTIC]
# select_all_statistics(days_ago=7): 통계 정보 가져오기
#  - days_ago일 전부터 현재까지의 통계 정보를 가져옴
#  - id, name(통계 이름), value(통계 값), date(날짜)로 구성
#  - name을 key로 하는 dict 형태로 반환
# create_statistic(data): 통계 생성
#  - name(통계 이름), value(통계 값), date(날짜)를 받아 통계 생성
#  - 만약 같은 name과 date를 가진 통계가 이미 존재하는 경우, value를 더함(+1)
##### [BLOCKED_IP]
# select_blocked_ips(): 차단된 IP 정보 가져오기
#  - id, ip(아이피)로 구성
# create_blocked_ip(data): IP 차단
#  - ip(아이피)를 받아 BLOCKED_IP에 추가
# delete_blocked_ip(ip): IP 차단 해제
#  - ip(아이피)를 받아 BLOCKED_IP에서 삭제
##### [BOARD & CATEGORY TREE]
# make_board_tree(group_name): 게시판 트리 생성
#  - parent_id를 사용하여 게시판 트리를 생성
#  - BOARD.display_groups에 group_name이 포함된 게시판만 가져옴(게시판 표시 권한 확인)
#  - 트리는 최대 4단계까지 생성될 수 있음
#  - 하위 노드가 업는 게시판은 제외(빈 노드는 표시하지 않음)
#  - id, name, display_groups, enter_groups, write_groups, comment_groups, children로 구성
# make_travel_board_tree(): 여행지 게시판 생성
#  - parent_id를 사용하여 여행지 게시판 트리를 생성
#  - BOARD.board_type이 'travel' 이거나 'tree'인 게시판만 가져옴
#  - 트리는 최대 4단계까지 생성될 수 있음
#  - 하위 노드가 업는 'tree' 게시판은 제외(빈 노드는 표시하지 않음)
#  - id, name, display_groups, enter_groups, write_groups, comment_groups, children로 구성
# select_board(board_id): 게시판 정보 가져오기
#  - id, name, board_type, display_groups, enter_groups, write_groups, comment_groups로 구성
#  - 해당 게시판의 정보만 가져옴
# create_board(data): 게시판 생성
#  - parent_board_id(상위 게시판), name, board_type, display_groups, enter_groups, write_groups, comment_groups를 받아 게시판 생성
#  - parent_board_id가 None인 경우 최상위 게시판으로 생성됨
# update_board(board_id, data): 게시판 정보 업데이트
#  - data에 포함되어있는 정보만 업데이트
#  - parent_board_id(상위 게시판), name, board_type, display_groups, enter_groups, write_groups, comment_groups를 받아 게시판 정보 업데이트
# delete_board(board_id): 게시판 삭제(하위 게시판이 있다면 전부 삭제. 게시글, 댓글, 관련 정보도 삭제)
#  - 게시판 삭제. 게시판을 삭제하면 나머지 정보는 cascade로 삭제됨.
#  - 하위 게시판이 있는 경우, 하위 게시판들의 parent_board_id를 None으로 변경해야함.
# make_category_tree(): 카테고리 트리 생성
#  - parent_id를 사용하여 카테고리 트리를 생성
#  - 카테고리 트리는 최대 4단계까지 생성될 수 있음
#  - id, name, children로 구성
# select_category(category_id): 카테고리 정보 가져오기
#  - id, name 구성
#  - 해당 카테고리의 정보만 가져옴
# create_category(data): 카테고리 생성
#  - parent_category_id(상위 카테고리), name을 받아 카테고리 생성
#  - parent_category_id가 None인 경우 최상위 카테고리로 생성됨
# update_category(category_id, data): 카테고리 정보 업데이트
#  - data에 포함되어있는 정보만 업데이트
#  - parent_category_id(상위 카테고리), name을 받아 카테고리 정보 업데이트
# delete_category(category_id): 카테고리 삭제(하위 카테고리가 있다면 전부 삭제. 게시글, 댓글, 관련 정보도 삭제)
#  - 카테고리 삭제. 카테고리를 삭제하면 나머지 정보는 cascade로 삭제됨.
#  - 하위 카테고리가 있는 경우, 하위 카테고리들의 parent_category_id를 None으로 변경해야함.




















####아래 코드는 업데이트 전 코드입니다. 업데이트 후 코드는 위에 있습니다.(2025-02-22일)
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