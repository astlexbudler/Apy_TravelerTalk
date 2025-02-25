import datetime
import random
import string
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, logout, get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q, Count, Case, When, Value, IntegerField
from django.conf import settings
from . import models

"""
####################
#  DAOS
아래 dao 함수들에 대해서는 권한을 확인할 필요는 없음. 권한 확인은 views에서 처리
page 파라메터를 받는 함수들은 반환 시 last_page도 함께 반환(페이지네이션을 위함) 예: return activities, last_page
##### [ACCOUNT]
get_default_contexts(request): 기본 컨텍스트 정보 가져오기
    - account, activities_preview, unread_messages, coupons_preview, best_reviews, server_settings 정보를 가져옴.
    - 각 항목은 사용자 정보, 사용자 활동 내역, 받은 메세지, 내 쿠폰, 베스트 리뷰, 서버 설정 정보로 구성됨.

select_account(account_id): 사용자 정보 가져오기
    - username(로그인 아이디), nickname(first_name 닉네임), partner_name(last_name 파트너 이름), email, group(그룹), status(상태), subsupervisor_permissions(부관리자 권한), level(레벨), exp(경험치), mileage(마일리지) 반환.
    - level 정보에는 level(레벨), image(레벨 이미지), text(레벨 텍스트), text_color(텍스트 색상), background_color(배경 색상) 포함.

select_account_detail(account_id): 사용자 상세 정보 가져오기(모든 정보)
    - select_account 정보를 포함하며 추가로 note(메모) 반환.

create_account(data): 사용자 생성
    - id, password, nickname, partner_name, email, group, account_type을 받아 사용자 생성.
    - exp, mileage는 SERVER_SETTING.register_point 값으로 초기화, level은 1로 설정.
    - account_type이 partner 또는 dame일 경우 status는 'pending', 그 외는 'active'로 설정.

update_account(account_id, data): 사용자 정보 업데이트
    - data에 포함된 정보만 업데이트.
    - password(set_password 사용), nickname(first_name), partner_name(last_name), email, status, note, subsupervisor_permissions, exp, mileage 업데이트.

delete_account(account_id): 사용자 삭제(모든 정보 삭제)
    - 사용자 정보 삭제. cascade로 관련 정보도 삭제됨.
    - 시스템 자동 삭제 시 사용, 사용자가 직접 삭제 시 30일 후 삭제(scheduler 처리).

search_accounts(nickname=None, id=None, any=None): 사용자 검색
    - nickname(first_name), id(username), any(닉네임 또는 아이디)로 검색.
    - username, nickname, status 반환.

##### [ACTIVITY]
get_account_activity_stats(account_id): 사용자 활동 통계 정보 가져오기
    - 작성한 리뷰, 게시글, 댓글, 출석체크한 날짜 수 확인

select_account_activities(account_id, page=1): 사용자 활동 내역 가져오기
    - id, message, exp_change, mileage_change, created_at 반환.
    - page당 20개 항목 가져옴.

create_account_activity(account_id, data): 사용자 활동 생성
    - message(활동 내용), exp_change(경험치 변화), mileage_change(마일리지 변화) 입력받아 생성.

##### [LEVEL]
select_level(level): 레벨 정보 가져오기
    - level, image, text, text_color, background_color 반환.

select_all_levels(): 모든 레벨 정보 가져오기
    - level, image, text, text_color, background_color 포함한 모든 레벨 반환.

create_level(data): 레벨 생성
    - level, image, text, text_color, background_color 입력받아 생성.

update_level(level, data): 레벨 정보 업데이트
    - data에 포함된 항목만 업데이트. level 값은 변경 불가.

##### [POST & PLACE_INFO]
search_posts(title=None, category_id=None, board_id=None, related_post_id=None, order='default', page=1): 게시글 검색
    - title(제목), category(카테고리), board(게시판)으로 검색.
    - page당 20개 가져오며, search_weight 및 created_at 기준 내림차순 정렬.
    - 반환값: id, author(작성자), related_post(관련 게시글), place_info(여행지 정보), boards(게시판), title, content, image, view_count, like_count, created_at, comment_count.

select_account_bookmarked_posts(account_id): 사용자 북마크한 게시글 가져오기
    - account에 북마크한 게시글 목록 반환.

select_post(post_id): 게시글 정보 가져오기
    - 게시글 상세 정보 반환.

create_post(data): 게시글 생성
    - author_id, related_post_id, title, content, image, board_ids 입력받아 생성.

update_post(post_id, data): 게시글 정보 업데이트
    - data 포함 항목만 업데이트.

delete_post(post_id): 게시글 삭제
    - 게시글 및 관련 정보 cascade 삭제.

create_post_place_info(data): 게시글의 여행지 정보 생성
    - post_id, category_ids, location_info, open_info, status 입력받아 생성.

update_place_info(post_id, data): 게시글의 여행지 정보 업데이트
    - data 포함 항목만 업데이트.

##### [COMMENT]
select_comments(post_id): 게시글 댓글 가져오기
    - post_id로 댓글 목록 반환.
    - id, account(작성자), content, created_at 포함.

create_comment(data): 댓글 생성
    - post_id, account_id, content 입력받아 생성.

update_comment(comment_id, data): 댓글 업데이트
    - content 업데이트.

delete_comment(comment_id): 댓글 삭제

##### [COUPON]
select_all_coupons(status=None): 모든 쿠폰 정보 가져오기
    - status에 따라 쿠폰 필터링.
    - code, related_post, name, content, image, expire_at, required_mileage, own_accounts, status 반환.

select_created_coupons(account_id, status=None): 사용자가 생성한 쿠폰 가져오기
select_owned_coupons(account_id, status=None): 사용자가 소유한 쿠폰 가져오기
    - status로 필터링하여 쿠폰 반환.

create_coupon(account_id, code, related_post_id, name, content, image, expire_at, required_mileage): 쿠폰 생성
update_coupon(coupon_id, data): 쿠폰 정보 업데이트

##### [MESSAGE]
select_received_messages(account_id, page=1): 받은 메세지 가져오기
select_sent_messages(account_id, page=1): 보낸 메세지 가져오기
    - title, sender/receiver, content, created_at, is_read, include_coupon 포함.

create_message(data): 메세지 생성
update_message(message_id, data): 메세지 업데이트

##### [SERVER_SETTING & UPLOAD]
select_all_server_settings(): 모든 서버 설정 가져오기
select_server_setting(name): 서버 설정 가져오기
update_server_setting(name, value): 서버 설정 업데이트
upload_file(file): 파일 업로드 및 경로 반환

##### [BANNER]
select_banners(): 배너 정보 가져오기
create_banner(data): 배너 생성
update_banner(banner_id, data): 배너 업데이트
delete_banner(banner_id): 배너 삭제

##### [STATISTIC]
select_all_statistics(days_ago=7): 통계 정보 가져오기
create_statistic(data): 통계 생성

##### [BLOCKED_IP]
select_blocked_ips(): 차단된 IP 목록 가져오기
create_blocked_ip(data): IP 차단
delete_blocked_ip(ip): IP 차단 해제

##### [BOARD & CATEGORY TREE]
make_board_tree(group_name): 게시판 트리 생성
make_travel_board_tree(): 여행지 게시판 트리 생성
select_board(board_id): 게시판 정보 가져오기
create_board(data): 게시판 생성
update_board(board_id, data): 게시판 업데이트
delete_board(board_id): 게시판 삭제

make_category_tree(): 카테고리 트리 생성
select_category(category_id): 카테고리 정보 가져오기
create_category(data): 카테고리 생성
update_category(category_id, data): 카테고리 업데이트
delete_category(category_id): 카테고리 삭제
"""




##### [ACCOUNT]
# 기본 컨텍스트 정보 가져오기
def get_default_contexts(request):
    return

# 사용자 정보 가져오기
def select_account(account_id):

    # 사용자 정보 확인
    account = models.ACCOUNT.objects.select_related(
        'level'
    ).prefetch_related(
        'bookmarked_posts', 'group'
    ).filter(
        id=account_id
    ).first()

    # 딕셔너리 형태로 포멧
    if account:
        return {
            'id': account.id,
            'username': account.username,
            'nickname': account.first_name,
            'account_type': account.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
            'status': account.status,
            'subsupervisor_permissions': str(account.subsupervisor_permissions).split(','),
            'level': select_level(account.level.level),
            'bookmarked_posts': [post.id for post in account.bookmarked_posts.all()],
            'exp': account.exp,
            'mileage': account.mileage,
        }
    else: # 사용자 정보가 없는 경우
        return None

# 사용자 상세 정보 가져오기(모든 정보)
def select_account_detail(account_id):

    # 사용자 정보 확인
    account = models.ACCOUNT.objects.select_related(
        'level'
    ).prefetch_related(
        'bookmarked_posts', 'group'
    ).filter(
        id=account_id
    ).first()

    # 딕셔너리 형태로 포멧
    if account:
        return {
            'id': account.id,
            'username': account.username,
            'nickname': account.first_name,
            'partner_name': account.last_name,
            'email': account.email,
            'account_type': account.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
            'status': account.status,
            'subsupervisor_permissions': str(account.subsupervisor_permissions).split(','),
            'level': select_level(account.level.level),
            'bookmarked_posts': [post.id for post in account.bookmarked_posts.all()],
            'exp': account.exp,
            'mileage': account.mileage,
            'note': account.note,
        }
    else: # 사용자 정보가 없는 경우
        return None

# 사용자 생성
def create_account(username, password, first_name, last_name, email, account_type):

    # 사용자 정보 확인(중복 확인)
    exist = models.ACCOUNT.objects.filter(
        Q(username=username) | Q(first_name=first_name) # 아이디 또는 닉네임 중복 확인
    ).exists()
    if exist:
        return {
            'success': False,
            'message': '이미 존재하는 사용자입니다.',
        }

    # 사용자 생성
    account = models.ACCOUNT.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    account.set_password(password)
    if account_type == 'user': # 사용자
        account.groups.add(Group.objects.get(name='user'))
        account.status = 'active'
    elif account_type == 'partner': # 파트너
        account.groups.add(Group.objects.get(name='partner'))
        account.status = 'pending'
    elif account_type == 'dame': # 여성 회원
        account.groups.add(Group.objects.get(name='dame'))
        account.status = 'pending'
    elif account_type == 'subsupervisor': # 부관리자
        account.groups.add(Group.objects.get(name='subsupervisor'))
        account.status = 'active'
    account.save()

    return {
        'success': True,
        'message': '사용자가 생성되었습니다.',
        'pk': account.id,
    }

# 사용자 정보 업데이트
def update_account(account_id, password=None, first_name=None, last_name=None, email=None, status=None, note=None, subsupervisor_permissions=None, exp=None, mileage=None):

    # 사용자 정보 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    )
    if not account.exists():
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 사용자 정보 업데이트
    account = account.first()
    if password: # 비밀번호 업데이트
        account.set_password(password)
    if first_name: # 닉네임 업데이트
        account.first_name = first_name
    if last_name: # 파트너 이름 업데이트
        account.last_name = last_name
    if email: # 이메일 업데이트
        account.email = email
    if status: # 상태 업데이트
        account.status = status
    if note: # 메모 업데이트
        account.note = note
    if subsupervisor_permissions: # 부관리자 권한 업데이트
        account.subsupervisor_permissions = subsupervisor_permissions
    if exp: # 경험치 업데이트
        account.exp = exp
    if mileage: # 마일리지 업데이트
        account.mileage = mileage
    account.save()

    return {
        'success': True,
        'message': '사용자 정보가 업데이트 되었습니다.',
        'pk': account.pk,
    }

# 사용자 삭제(모든 정보 삭제)
def delete_account(account_id):

    # 사용자 정보 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    )
    if not account.exists():
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 사용자 정보 삭제
    account = account.first()
    if account.is_active: # 사용자가 직접 삭제한 경우
        account.status = 'deleted'
        account.is_active = False
        account.save()
    else: # 시스템이 자동 삭제한 경우
        account.delete() # 사용자가 생성한 데이터는 cascade로 삭제됨

    return {
        'success': True,
        'message': '사용자 정보가 삭제되었습니다.',
    }

# 사용자 검색
def search_accounts(username=None, nickname=None, any=None, status=None, account_type=None, page=1):

    # 사용자 정보 확인
    accounts = models.ACCOUNT.objects.select_related('level').prefetch_related('group')
    query = Q()

    if username:
        query &= Q(username__icontains=username)
    if nickname:
        query &= Q(first_name__icontains=nickname)
    if any:
        query &= Q(username__icontains=any) | Q(first_name__icontains=any)
    if status:
        query &= Q(status=status)
    if account_type:
        query &= Q(group__name=account_type)

    accounts = accounts.filter(query).order_by('-date_joined')

    # 페이지네이션
    last_page = (accounts.count() // 20) + 1
    accounts = accounts[(page-1)*20:page*20]

    # 사용자 정보 포멧
    accounts_data = [{
        'id': account.id,
        'username': account.username,
        'nickname': account.first_name,
        'partner_name': account.last_name,
        'account_type': account.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
        'status': account.status,
        'subsupervisor_permissions': str(account.subsupervisor_permissions).split(','),
        'level': select_level(account.level.level),
        'exp': account.exp,
        'mileage': account.mileage,
    } for account in accounts]

    return accounts_data, last_page



##### [ACTIVITY]
# 사용자 활동 통계 정보 가져오기
def get_account_activity_stats(account_id, page=1):

    # 사용자 활동 통계 정보 확인
    activities = models.ACTIVITY.objects.select_related(
        'account'
    ).filter(
        account__id=account_id
    )

    # 작성한 리뷰
    review_count = activities.filter(
        message='리뷰 작성'
    ).count()

    # 작성한 게시글
    post_count = activities.filter(
        message='게시글 작성'
    ).count()

    # 작성한 댓글
    comment_count = activities.filter(
        message='댓글 작성'
    ).count()

    # 출석체크한 날짜 수
    check_count = activities.filter(
        message='출석체크'
    ).count()

    return {
        'review_count': review_count,
        'post_count': post_count,
        'comment_count': comment_count,
        'check_count': check_count,
    }

# 사용자 활동 내역 가져오기
def select_account_activities(account_id, page=1):

    # 사용자 활동 내역 확인
    activities = models.ACTIVITY.objects.select_related(
        'account'
    ).filter(
        account__id=account_id
    )

    # 페이지네이션
    last_page = (activities.count() // 20) + 1
    activities = activities[(page-1)*20:page*20]

    # 사용자 활동 내역 포멧
    activities_data = [{
        'id': activity.id,
        'message': activity.message,
        'exp_change': activity.exp_change,
        'mileage_change': activity.mileage_change,
        'created_at': activity.created_at,
    } for activity in activities]

    return activities_data, last_page

# 사용자 활동 생성
def create_account_activity(account_id, message, exp_change, mileage_change):

    # 사용자 정보 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    ).first()
    if not account:
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 사용자 활동 생성
    activity = models.ACTIVITY.objects.create(
        account=account,
        message=message,
        exp_change=exp_change,
        mileage_change=mileage_change,
    )

    return {
        'success': True,
        'message': '사용자 활동이 생성되었습니다.',
        'pk': activity.id,
    }



##### [LEVEL]
# 레벨 정보 가져오기
def select_level(level):

    # 레벨 정보 확인
    level = models.LEVEL_RULE.objects.filter(
        level=level
    ).first()

    # 딕셔너리 형태로 포멧
    if level:
        return {
            'level': level.level,
            'image': level.image,
            'text': level.text,
            'text_color': level.text_color,
            'background_color': level.background_color,
        }
    else: # 레벨 정보가 없는 경우
        return None

# 모든 레벨 정보 가져오기
def select_all_levels():

    # 모든 레벨 정보 확인
    levels = models.LEVEL_RULE.objects.all()

    # 딕셔너리 형태로 포멧
    levels_data = [{
        'level': level.level,
        'image': level.image,
        'text': level.text,
        'text_color': level.text_color,
        'background_color': level.background_color,
    } for level in levels]

    return levels_data

# 레벨 생성
def create_level(level, image, text, text_color, background_color):

    # 레벨 확인
    exist = models.LEVEL_RULE.objects.filter(
        level=level
    ).exists()
    if exist:
        return {
            'success': False,
            'message': '이미 존재하는 레벨입니다.',
        }

    # 레벨 생성
    level = models.LEVEL_RULE.objects.create(
        level=level,
        image=image,
        text=text,
        text_color=text_color,
        background_color=background_color,
    )

    return {
        'success': True,
        'message': '레벨이 생성되었습니다.',
        'pk': level.level,
    }

# 레벨 정보 업데이트
def update_level(level, image=None, text=None, text_color=None, background_color=None):

    # 레벨 정보 확인
    level = models.LEVEL_RULE.objects.filter(
        level=level
    )
    if not level.exists():
        return {
            'success': False,
            'message': '레벨 정보가 존재하지 않습니다.',
        }

    # 레벨 정보 업데이트
    level = level.first()
    if image: # 이미지 업데이트
        level.image = image
    if text: # 텍스트 업데이트
        level.text = text
    if text_color: # 텍스트 색상 업데이트
        level.text_color = text_color
    if background_color: # 배경 색상 업데이트
        level.background_color = background_color
    level.save()

    return {
        'success': True,
        'message': '레벨 정보가 업데이트 되었습니다.',
        'pk': level.level,
    }



##### [POST & PLACE_INFO]
# 게시글 검색
def search_posts(title=None, category_id=None, board_id=None, related_post_id=None, order='default', page=1):

    # 게시글 정보 확인
    posts = models.POST.objects.select_related(
        'author' 'related_post', 'place_info'
    ).prefetch_related(
        'boards', 'place_info__categories'
    )
    query = Q()

    if title:
        query &= Q(title__icontains=title)
    if category_id:
        query &= Q(place_info__categories__id__in=[category_id])
    if board_id:
        query &= Q(boards__id__in=[board_id])
    if related_post_id:
        query &= Q(related_post__id=related_post_id)

    posts = posts.filter(query)

    # 정렬
    if order == 'best':
        posts = posts.filter(query).annotate(
            ad_priority=Case(
                When(place_info__status='ad', then=Value(0)),   # 'ad' 상태일 때 우선순위 0
                default=Value(1),                                # 그 외는 우선순위 1
                output_field=IntegerField(),
            )
        ).order_by('ad_priority', '-search_weight', '-created_at')
    elif order == 'default':
        posts = posts.filter(query).order_by('-created_at')

    # 페이지네이션
    last_page = (posts.count() // 20) + 1
    posts = posts[(page-1)*20:page*20]

    # 게시글 정보 포멧
    posts_data = [{
        'id': post.id,
        'author': {
            'nickname': post.author.last_name,
            'partner_name': post.author.first_name,
        },
        'related_post': {
            'id': post.related_post.id,
            'title': post.related_post.title,
        } if post.related_post else None,
        'place_info': {
            'categories': [{
                'id': c.id,
                'name': c.name,
            } for c in post.place_info.categories.all()],
            'category_ids': [c.id for c in post.place_info.categories.all()],
            'location_info': post.place_info.location_info,
            'open_info': post.place_info.open_info,
            'status': post.place_info.status,
        } if post.place_info else None,
        'boards': [{
            'id': board.id,
            'name': board.name,
        } for board in post.boards.all()],
        'board_ids': [board.id for board in post.boards.all()],
        'title': post.title,
        'image': post.image,
        'view_count': post.view_count,
        'like_count': post.like_count,
        'created_at': post.created_at,
        'comment_count': models.COMMENT.objects.filter(post=post).count(),
    } for post in posts]

    return posts_data, last_page

# 사용자 북마크한 게시글 가져오기
def select_account_bookmarked_posts(account_id):

    # 사용자 확인
    account = models.ACCOUNT.objects.prefetch_related(
        'bookmarked_posts'
    ).select_related(
        'bookmarked_posts__author', 'bookmarked_posts__related_post', 'bookmarked_posts__place_info'
    ).prefetch_related(
        'bookmarked_posts__boards', 'bookmarked_posts__place_info__categories'
    ).filter(
        id=account_id
    )
    if not account.exists():
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 사용자 북마크한 게시글 확인
    posts = account.first().bookmarked_posts.all()

    # 게시글 정보 포멧
    posts_data = [{
        'id': post.id,
        'author': {
            'nickname': post.author.last_name,
            'partner_name': post.author.first_name,
        },
        'related_post': {
            'id': post.related_post.id,
            'title': post.related_post.title,
        } if post.related_post else None,
        'place_info': {
            'categories': [{
                'id': c.id,
                'name': c.name,
            } for c in post.place_info.categories.all()],
            'category_ids': [c.id for c in post.place_info.categories.all()],
            'location_info': post.place_info.location_info,
            'open_info': post.place_info.open_info,
            'status': post.place_info.status,
        } if post.place_info else None,
        'boards': [{
            'id': board.id,
            'name': board.name,
        } for board in post.boards.all()],
        'board_ids': [board.id for board in post.boards.all()],
        'title': post.title,
        'image': post.image,
        'view_count': post.view_count,
        'like_count': post.like_count,
        'created_at': post.created_at,
        'comment_count': models.COMMENT.objects.filter(post=post).count(),
    } for post in posts]

    return posts_data

# 게시글 정보 가져오기
def select_post(post_id):

    # 게시글 정보 확인
    post = models.POST.objects.select_related(
        'author', 'related_post', 'place_info'
    ).prefetch_related(
        'boards', 'place_info__categories'
    ).filter(
        id=post_id
    ).first()
    if not post:
        return {
            'success': False,
            'message': '게시글 정보가 존재하지 않습니다.',
        }

    # 게시글 정보 포멧
    post_data = {
        'id': post.id,
        'author': {
            'nickname': post.author.last_name,
            'partner_name': post.author.first_name,
        },
        'related_post': {
            'id': post.related_post.id,
            'title': post.related_post.title,
        } if post.related_post else None,
        'place_info': {
            'categories': [{
                'id': c.id,
                'name': c.name,
            } for c in post.place_info.categories.all()],
            'category_ids': [c.id for c in post.place_info.categories.all()],
            'location_info': post.place_info.location_info,
            'open_info': post.place_info.open_info,
            'status': post.place_info.status,
        } if post.place_info else None,
        'boards': [{
            'id': board.id,
            'name': board.name,
        } for board in post.boards.all()],
        'board_ids': [board.id for board in post.boards.all()],
        'title': post.title,
        'content': post.content,
        'image': post.image,
        'view_count': post.view_count,
        'like_count': post.like_count,
        'created_at': post.created_at,
        'comment_count': models.COMMENT.objects.filter(post=post).count(),
    }

    return post_data

# 게시글 생성
def create_post(author_id, related_post_id, title, content, image, board_ids):

    # 사용자 확인
    account = models.ACCOUNT.objects.filter(
        id=author_id
    )
    if not account.exists():
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # related_post 확인
    if related_post_id:
        related_post = models.POST.objects.filter(
            id=related_post_id
        )
        if not related_post.exists():
            return {
                'success': False,
                'message': '관련 게시글 정보가 존재하지 않습니다.',
            }

    # board_ids 확인
    boards = []
    board_ids = str(board_ids).split(',')
    for board_id in board_ids:
        board = models.BOARD.objects.filter(
            id=board_id
        )
        if not board.exists():
            return {
                'success': False,
                'message': '게시판 정보가 존재하지 않습니다.',
            }
        else:
            boards.append(board.first())

    # 게시글 생성
    post = models.POST.objects.create(
        author=account.first(),
        related_post=related_post.first() if related_post_id else None,
        title=title,
        content=content,
        image=image,
    )
    post.boards.set(boards)
    post.save()

    return {
        'success': True,
        'message': '게시글이 생성되었습니다.',
        'pk': post.id,
    }

# 게시글의 여행지 정보 생성
def create_post_place_info(post_id, category_ids, location_info, open_info, status):

    # 게시글 확인
    post = models.POST.objects.filter(
        id=post_id
    )
    if not post.exists():
        return {
            'success': False,
            'message': '게시글 정보가 존재하지 않습니다.',
        }

    # category_ids 확인
    categories = []
    for category_id in category_ids:
        category = models.CATEGORY.objects.filter(
            id=category_id
        )
        if not category.exists():
            return {
                'success': False,
                'message': '카테고리 정보가 존재하지 않습니다.',
            }
        else:
            categories.append(category.first())

    # 게시글의 여행지 정보 생성
    place_info = models.PLACE_INFO.objects.create(
        post=post.first(),
        location_info=location_info,
        open_info=open_info,
        status=status,
    )
    place_info.categories.set(categories)
    place_info.save()

    return {
        'success': True,
        'message': '게시글의 여행지 정보가 생성되었습니다.',
        'pk': place_info.id,
    }

# 게시글 정보 업데이트
def update_post(post_id, title=None, content=None, image=None, board_ids=None, search_weight=None, view_count=None, like_count=None):

    # 게시글 확인
    post = models.POST.objects.filter(
        id=post_id
    )
    if not post.exists():
        return {
            'success': False,
            'message': '게시글 정보가 존재하지 않습니다.',
        }

    # board_ids 확인
    boards = []
    if board_ids:
        board_ids = str(board_ids).split(',')
        for board_id in board_ids:
            board = models.BOARD.objects.filter(
                id=board_id
            )
            if not board.exists():
                return {
                    'success': False,
                    'message': '게시판 정보가 존재하지 않습니다.',
                }
            else:
                boards.append(board.first())

    # 게시글 정보 업데이트
    post = post.first()
    if title: # 제목 업데이트
        post.title = title
    if content: # 내용 업데이트
        post.content = content
    if image: # 이미지 업데이트
        post.image = image
    if boards: # 게시판 업데이트
        post.boards.set(boards)
    if search_weight: # 검색 가중치 업데이트
        post.search_weight = search_weight
    if view_count: # 조회수 업데이트
        post.view_count = view_count
    if like_count: # 좋아요 수 업데이트
        post.like_count = like_count
    post.save()

    return {
        'success': True,
        'message': '게시글 정보가 업데이트 되었습니다.',
        'pk': post.id,
    }

# 게시글의 여행지 정보 업데이트
def update_place_info(post_id, category_ids=None, location_info=None, open_info=None, status=None, ad_start_at=None, ad_end_at=None, note=None):

    # 게시글 확인
    post = models.POST.objects.filter(
        id=post_id
    )
    if not post.exists():
        return {
            'success': False,
            'message': '게시글 정보가 존재하지 않습니다.',
        }

    # category_ids 확인
    categories = []
    if category_ids:
        for category_id in category_ids:
            category = models.CATEGORY.objects.filter(
                id=category_id
            )
            if not category.exists():
                return {
                    'success': False,
                    'message': '카테고리 정보가 존재하지 않습니다.',
                }
            else:
                categories.append(category.first())

    # 게시글의 여행지 정보 확인
    place_info = models.PLACE_INFO.objects.filter(
        post=post.first()
    )
    if not place_info.exists():
        return {
            'success': False,
            'message': '게시글의 여행지 정보가 존재하지 않습니다.',
        }

    # 게시글의 여행지 정보 업데이트
    place_info = place_info.first()
    if categories: # 카테고리 업데이트
        place_info.categories.set(categories)
    if location_info: # 위치 정보 업데이트
        place_info.location_info = location_info
    if open_info: # 오픈 정보 업데이트
        place_info.open_info = open_info
    if status: # 상태 업데이트
        place_info.status = status
    if ad_start_at: # 광고 시작일 업데이트
        place_info.ad_start_at = ad_start_at
    if ad_end_at: # 광고 종료일 업데이트
        place_info.ad_end_at = ad_end_at
    if note: # 메모 업데이트
        place_info.note = note
    place_info.save()

    return {
        'success': True,
        'message': '게시글의 여행지 정보가 업데이트 되었습니다.',
        'pk': place_info.id,
    }

# 게시글 삭제
def delete_post(post_id):

    # 게시글 삭제
    post = models.POST.objects.filter(
        id=post_id
    ).first()
    post.delete()

    return {
        'success': True,
        'message': '게시글이 삭제되었습니다.',
    }



##### [COMMENT]
# 게시글 댓글 가져오기
def select_comments(post_id):

    # 게시글 확인
    post = models.POST.objects.filter(
        id=post_id
    )
    if not post.exists():
        return {
            'success': False,
            'message': '게시글 정보가 존재하지 않습니다.',
        }

    # 게시글 댓글 확인
    comments = models.COMMENT.objects.select_related(
        'author'
    ).filter(
        post=post.first()
    )

    # 게시글 댓글 포멧
    comments_data = [{
        'id': comment.id,
        'author': {
            'nickname': comment.author.last_name,
            'partner_name': comment.author.first_name,
        },
        'content': comment.content,
        'created_at': comment.created_at,
    } for comment in comments]

    return comments_data

# 댓글 생성
def create_comment(post_id, account_id, content):

    # 게시글 확인
    post = models.POST.objects.filter(
        id=post_id
    )
    if not post.exists():
        return {
            'success': False,
            'message': '게시글 정보가 존재하지 않습니다.',
        }

    # 사용자 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    )
    if not account.exists():
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 댓글 생성
    comment = models.COMMENT.objects.create(
        post=post.first(),
        author=account.first(),
        content=content,
    )

    return {
        'success': True,
        'message': '댓글이 생성되었습니다.',
        'pk': comment.id,
    }

# 댓글 업데이트
def update_comment(comment_id, content):

    # 댓글 확인
    comment = models.COMMENT.objects.filter(
        id=comment_id
    )
    if not comment.exists():
        return {
            'success': False,
            'message': '댓글 정보가 존재하지 않습니다.',
        }

    # 댓글 업데이트
    comment = comment.first()
    comment.content = content
    comment.save()

    return {
        'success': True,
        'message': '댓글이 업데이트 되었습니다.',
        'pk': comment.id,
    }

# 댓글 삭제
def delete_comment(comment_id):

    # 댓글 삭제
    comment = models.COMMENT.objects.filter(
        id=comment_id
    ).first()
    comment.delete()

    return {
        'success': True,
        'message': '댓글이 삭제되었습니다.',
    }



##### [COUPON]
# 모든 쿠폰 정보 가져오기
def select_all_coupons(status=None):

    # 모든 쿠폰 정보 확인
    coupons = models.COUPON.objects.select_related(
        'own_account', 'related_post', 'created_account', 'own_account__level',
    ).prefetch_related(
        'created_account__group'
    ).filter(
        status=status
    )

    # 정렬
    coupons = coupons.order_by('-created_at')

    # 쿠폰 정보 포멧
    coupons_data = [{
        'code': coupon.code,
        'related_post': {
            'id': coupon.related_post.id,
            'title': coupon.related_post.title,
        } if coupon.related_post else None,
        'name': coupon.name,
        'content': coupon.content,
        'image': coupon.image,
        'expire_at': coupon.expire_at,
        'required_mileage': coupon.required_mileage,
        'own_account': {
            'id': coupon.own_account.id,
            'nickname': coupon.own_account.first_name,
            'level': select_level(coupon.own_account.level.level),
        } if coupon.own_account else None,
        'created_account': {
            'id': coupon.created_account.id,
            'nickname': coupon.created_account.first_name,
            'partner_name': coupon.created_account.last_name,
            'account_type': coupon.created_account.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
        } if coupon.created_account else None,
        'status': coupon.status,
        'note': coupon.note,
    } for coupon in coupons]

    return coupons_data

# 사용자가 생성한 쿠폰 정보 가져오기
def select_created_coupons(account_id, status=None):

    # 사용자 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    )
    if not account.exists():
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 사용자가 생성한 쿠폰 정보 확인
    coupons = models.COUPON.objects.select_related(
        'own_account', 'related_post', 'created_account', 'own_account__level',
    ).prefetch_related(
        'created_account__group'
    ).filter(
        created_account=account.first(),
        status=status
    )

    # 정렬
    coupons = coupons.order_by('-created_at')

    # 쿠폰 정보 포멧
    coupons_data = [{
        'code': coupon.code,
        'related_post': {
            'id': coupon.related_post.id,
            'title': coupon.related_post.title,
        } if coupon.related_post else None,
        'name': coupon.name,
        'content': coupon.content,
        'image': coupon.image,
        'expire_at': coupon.expire_at,
        'required_mileage': coupon.required_mileage,
        'own_account': {
            'id': coupon.own_account.id,
            'nickname': coupon.own_account.first_name,
            'level': select_level(coupon.own_account.level.level),
        } if coupon.own_account else None,
        'created_account': {
            'id': coupon.created_account.id,
            'nickname': coupon.created_account.first_name,
            'partner_name': coupon.created_account.last_name,
            'account_type': coupon.created_account.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
        } if coupon.created_account else None,
        'status': coupon.status,
        'note': coupon.note,
    } for coupon in coupons]

    return coupons_data

# 사용자가 소유한 쿠폰 정보 가져오기
def select_owned_coupons(account_id, status=None):

    # 사용자 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    )
    if not account.exists():
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 사용자가 소유한 쿠폰 정보 확인
    coupons = models.COUPON.objects.select_related(
        'own_account', 'related_post', 'created_account', 'own_account__level',
    ).prefetch_related(
        'created_account__group'
    ).filter(
        own_account=account.first(),
        status=status
    )

    # 정렬
    coupons = coupons.order_by('-created_at')

    # 쿠폰 정보 포멧
    coupons_data = [{
        'code': coupon.code,
        'related_post': {
            'id': coupon.related_post.id,
            'title': coupon.related_post.title,
        } if coupon.related_post else None,
        'name': coupon.name,
        'content': coupon.content,
        'image': coupon.image,
        'expire_at': coupon.expire_at,
        'required_mileage': coupon.required_mileage,
        'own_account': {
            'id': coupon.own_account.id,
            'nickname': coupon.own_account.first_name,
            'level': select_level(coupon.own_account.level.level),
        } if coupon.own_account else None,
        'created_account': {
            'id': coupon.created_account.id,
            'nickname': coupon.created_account.first_name,
            'partner_name': coupon.created_account.last_name,
            'account_type': coupon.created_account.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
        } if coupon.created_account else None,
        'status': coupon.status,
        'note': coupon.note,
    } for coupon in coupons]

    return coupons_data

# 쿠폰 생성
def create_coupon(account_id, code, related_post_id, name, content, image, expire_at, required_mileage):

    # 사용자 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    )
    if not account.exists():
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # related_post 확인
    related_post = models.POST.objects.filter(
        id=related_post_id
    )
    if not related_post.exists():
        return {
            'success': False,
            'message': '관련 게시글 정보가 존재하지 않습니다.',
        }

    # 코드 중복 확인
    exist = models.COUPON.objects.filter(
        code=code
    ).exists()
    if exist:
        return {
            'success': False,
            'message': '이미 존재하는 코드입니다.',
        }

    # 쿠폰 생성
    coupon = models.COUPON.objects.create(
        code=code,
        related_post=related_post.first(),
        name=name,
        content=content,
        image=image,
        expire_at=expire_at,
        required_mileage=required_mileage,
        created_account=account.first(),
    )

    return {
        'success': True,
        'message': '쿠폰이 생성되었습니다.',
        'pk': coupon.code,
    }

# 쿠폰 정보 업데이트
def update_coupon(code, name=None, content=None, image=None, expire_at=None, required_mileage=None, own_account_id=None, status=None, note=None):

    # 쿠폰 확인
    coupon = models.COUPON.objects.filter(
        code=code
    )
    if not coupon.exists():
        return {
            'success': False,
            'message': '쿠폰 정보가 존재하지 않습니다.',
        }

    # 사용자 확인
    own_account = models.ACCOUNT.objects.filter(
        id=own_account_id
    )
    if own_account_id and not own_account.exists():
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 쿠폰 정보 업데이트
    coupon = coupon.first()
    if name: # 이름 업데이트
        coupon.name = name
    if content: # 내용 업데이트
        coupon.content = content
    if image: # 이미지 업데이트
        coupon.image = image
    if expire_at: # 만료일 업데이트
        coupon.expire_at = expire_at
    if required_mileage: # 필요 마일리지 업데이트
        coupon.required_mileage = required_mileage
    if own_account_id: # 소유자 업데이트
        coupon.own_account = own_account.first()
    if status: # 상태 업데이트
        coupon.status = status
    if note: # 메모 업데이트
        coupon.note = note
    coupon.save()

    return {
        'success': True,
        'message': '쿠폰 정보가 업데이트 되었습니다.',
        'pk': coupon.code,
    }



##### [MESSAGE]
# 사용자가 받은 메세지 가져오기
def select_received_messages(account_id, page=1):

    # 사용자 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    )
    if not account.exists():
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 사용자가 받은 메세지 확인
    messages = models.MESSAGE.objects.filter(
        to_account=account_id
    )

    # 정렬
    messages = messages.order_by('-created_at')

    # 페이지네이션
    last_page = (messages.count() // 20) + 1
    messages = messages[(page-1)*20:page*20]

    # 메세지 정보 포멧
    for message in messages:
        from_account = None
        to_account = None
        # TODO: 내일 이어서 작업

    return

# 사용자가 보낸 메세지 가져오기
def select_sent_messages(account_id, page=1):
    return

# 메세지 생성
def create_message(sender_id, receiver_id, title, content, image, include_coupon_code):
    return

# 메세지 정보 업데이트(읽음 처리)
def update_message(message_id):
    return



##### [SERVER_SETTING & UPLOAD]
# 모든 서버 설정 가져오기
def select_all_server_settings():
    return

# 서버 설정 가져오기
def select_server_setting(name):
    return

# 서버 설정 업데이트
def update_server_setting(name, value):
    return

# 파일 업로드 및 경로 반환
def upload_file(file):
    return



##### [BANNER]
# 배너 정보 가져오기
def select_banners():
    return

# 배너 생성
def create_banner(image, link, display_weight, location, size):
    return

# 배너 정보 업데이트
def update_banner(banner_id, image=None, link=None, display_weight=None, location=None, size=None):
    return

# 배너 삭제
def delete_banner(banner_id):
    return



##### [STATISTIC]
# 통계 정보 가져오기
def select_all_statistics(days_ago=7):
    return

# 통계 생성
def create_statistic(name, value, date):
    return



##### [BLOCKED_IP]
# 차단된 IP 정보 가져오기
def select_blocked_ips():
    return

# IP 차단
def create_blocked_ip(ip):
    return

# IP 차단 해제
def delete_blocked_ip(ip):
    return



##### [BOARD & CATEGORY TREE]
# 게시판 트리 생성
def make_board_tree(group_name):
    return

# 여행지 게시판 생성
def make_travel_board_tree():
    return

# 게시판 정보 가져오기
def select_board(board_id):
    return

# 게시판 생성
def create_board(parent_board_id, name, board_type, display_groups, enter_groups, write_groups, comment_groups, level_cut):
    return

# 게시판 정보 업데이트
def update_board(board_id, parent_board_id=None, name=None, board_type=None, display_groups=None, enter_groups=None, write_groups=None, comment_groups=None, level_cut=None):
    return

# 게시판 삭제 및 하위 게시판 초기화
def delete_board(board_id):
    return

# 카테고리 트리 생성
def make_category_tree():
    return

# 카테고리 정보 가져오기
def select_category(category_id):
    return

# 카테고리 생성
def create_category(parent_category_id, name):
    return

# 카테고리 정보 업데이트
def update_category(category_id, parent_category_id=None, name=None):
    return

# 카테고리 삭제 및 하위 카테고리 초기화
def delete_category(category_id):
    return






















####아래 코드는 업데이트 전 코드입니다. 업데이트 후 코드는 위에 있습니다.(2025-02-22일)
# 기본 컨텍스트 정보 가져오기
def get_default_contexts(request):
  if request.user.is_authenticated: # 로그인 되어있는 경우
    # 사용자 정보 가져오기
    user = get_user_model().objects.select_related('level').prefetch_related('bookmarked_posts').get(username=request.user.username)

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
      'bookmarked_posts': [{
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
      } for bp in user.bookmarked_posts.all()[:5]],
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
def get_all_bookmarked_posts(user_id):
  bookmarks = models.ACCOUNT.objects.prefetch_related('bookmarked_posts').prefetch_related('bookmarked_posts__place_info__categories',).get(
    username=user_id
  ).bookmarked_posts.all()
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