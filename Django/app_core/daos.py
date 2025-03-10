import datetime
import math
import random
import string
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, logout, get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q, Count, Case, When, Value, IntegerField
from django.conf import settings
from django.contrib.auth.models import Group
from . import models

"""
####################
#  DAOS
get_default_contexts(request): 기본 컨텍스트 정보 가져오기
get_urls(): URL 정보 가져오기
##### [ACCOUNT]
select_account(account_id): 사용자 정보 가져오기
select_account_detail(account_id): 사용자 상세 정보 가져오기(모든 정보)
select_accounts(nickname=None, id=None, any=None, account_type=None, status=None, page=1): 사용자 검색
create_account(username, password, nickname, account_type, partner_name=None, email=None, tel=None): 사용자 생성
update_account(account_id, password=None, nickname=None, partner_name=None, email=None, tel=None, status=None, note=None, subsupervisor_permissions=None, exp=None, mileage=None, recent_ip=None): 사용자 정보 업데이트
delete_account(account_id): 사용자 삭제(처음은 is_active=False로 변경, 다음은 cascade 삭제)

##### [ACTIVITY]
account_activity_stats(account_id): 사용자 활동 통계 정보 가져오기
select_account_activities(account_id, page=1): 사용자 활동 내역 가져오기
create_account_activity(account_id, message, exp_change=0, mileage_change=0): 사용자 활동 생성

##### [LEVEL]
select_level(level): 레벨 정보 가져오기
select_all_levels(): 모든 레벨 정보 가져오기
create_level(level, required_exp, text=None, text_color=None, background_color=None, image=None): 레벨 생성
update_level(level, text=None, text_color=None, background_color=None, required_exp=None, image=None): 레벨 정보 업데이트

##### [POST & PLACE_INFO]
select_posts(title=None, category_id=None, board_id=None, related_post_id=None, order='default', place_info_status=None, author_nickname=None, author_partner_name=None, min_search_weight=0, page=1): 게시글 검색
select_account_bookmarked_posts(account_id): 사용자 북마크한 게시글 가져오기
select_post(post_id): 게시글 정보 가져오기
create_post(title, board_ids, author_id, content, related_post_id=None, image=None, include_coupons=None, hide=False): 게시글 생성
update_post(post_id, title=None, content=None, board_ids₩
create_post_place_info(post_id, category_ids, location_info, open_info, address): 게시글의 여행지 정보 생성
update_place_info(place_info_id, category_ids=None, location_info=None, open_info=None, address=None, status=None, note=None): 여행지 정보 업데이트
delete_place_info(post_id): 게시글의 여행지 정보 삭제

##### [COMMENT]
select_comments(post_id, page=None): 게시글 댓글 가져오기
create_comment(post_id, account_id, content, hide=False): 댓글 생성
update_comment(comment_id, content, hide): 댓글 업데이트
delete_comment(comment_id): 댓글 삭제

##### [COUPON]
select_coupons(code=None, name=None, status=None, related_post_id=None, create_account_partner_name=None, own_account_nickname=None, page=1): 쿠폰 검색
select_coupon(coupon_id): 쿠폰 정보 가져오기
create_coupon(account_id, code, related_post_id, name, content, image, expire_at, required_mileage): 쿠폰 생성
update_coupon(coupon_code, name=None, content=None, image=None, expire_at=None, required_mileage=None, status=None, note=None): 쿠폰 정보 업데이트

##### [MESSAGE]
select_message(message_id): 메세지 정보 가져오기
select_messages(receive_account_id=None, sender_account_id=None, is_read=None, message_type=None page=1): 메세지 검색
create_message(receive_account_id, sender_account_id, title, content, message_type, image=None, include_coupon=None): 메세지 생성
update_message(message_id, delete_coupon=False): 메세지 정보 업데이트

##### [SERVER_SETTING & UPLOAD]
select_server_settings(): 모든 서버 설정 가져오기
select_server_setting(name): 서버 설정 가져오기
update_server_setting(name, value): 서버 설정 업데이트
upload_file(file): 파일 업로드 및 경로 반환

##### [BANNER]
select_banners(location): 배너 정보 가져오기
create_banner(location, image, link, status, display_weight): 배너 생성
update_banner(banner_id, location=None, image=None, link=None, status=None, display_weight=None): 배너 정보 업데이트
delete_banner(banner_id): 배너 삭제

##### [STATISTIC]
get_statistics(days_ago=7): 통계 정보 가져오기
set_statistic(name, date): 통계 생성(또는 업데이트)

##### [Blocked_IP]
select_blocked_ips(): 차단된 IP 목록 가져오기
create_blocked_ip(ip): IP 차단
delete_blocked_ip(ip): IP 차단 해제

##### [BOARD & CATEGORY TREE]
make_board_tree(account_type, board_type): 게시판 트리 생성
select_board(board_id): 게시판 정보 가져오기
create_board(display_groups, write_groups, comment_groups, name, board_type, parent_board=None, level_cut=0, search_weight=0): 게시판 생성
update_board(board_id, display_groups=None, write_groups=None, comment_groups=None, name=None, parent_board=None, level_cut=None, search_weight=None, board_type=None): 게시판 업데이트
delete_board(board_id): 게시판 삭제

make_category_tree(): 카테고리 트리 생성
select_category(category_id): 카테고리 정보 가져오기
create_category(parent_id, name, display_weight): 카테고리 생성
update_category(category_id, name=None, display_weigh=None, parent_category_id=None): 카테고리 업데이트
delete_category(category_id): 카테고리 삭제
"""

def get_default_contexts(request):

    # 사용자 정보 확인
    if not request.user.is_authenticated: # 비로그인 사용자
        account = {
            'id': '',
            'account_type': 'guest',
            'level': {
                'level': 0
            }
        }
        activities_preview = []
        unread_messages = []
        coupons_preview = []
        best_reviews = []
        bookmarks = []
    else:
        account = select_account(request.user.id)
        activities_preview = select_account_activities(account['id'], page=1)[0][:5]
        unread_messages = select_messages(receive_account_id=account['id'], is_read=False, page=1)[0][:5]
        coupons_preview = select_coupons(own_account_id=account['id'], status='active', page=1)[0][:5]
        best_reviews = select_posts(order='best', page=1, board_id='38')[0][:5]
        bookmarks = select_account_bookmarked_posts(account['id'])[:5]

    # 서버 설정 정보 확인
    server_settings = {
        'site_logo': select_server_setting('site_logo'),
        'service_name': select_server_setting('service_name'),
        'company_info': select_server_setting('company_info'),
    }

    return {
        **get_urls(),
        'account': account,
        'activities_preview': activities_preview,
        'unread_messages': unread_messages,
        'coupons_preview': coupons_preview,
        'best_reviews': best_reviews,
        'server_settings': server_settings,
        'bookmarks': bookmarks,
    }

# URL 정보 가져오기
def get_urls():
    return {
        'MAIN_URL': settings.MAIN_URL,
        'SUPERVISOR_URL': settings.SUPERVISOR_URL,
        'PARTNER_URL': settings.PARTNER_URL,
    }



##### [ACCOUNT]
# 사용자 정보 가져오기
def select_account(account_id):

    # 사용자 정보 확인
    account = models.ACCOUNT.objects.exclude(
        status='deleted'
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
            'level': select_level(account.level.pk),
            'bookmarked_posts': [post.id for post in account.bookmarked_posts.all()],
            'exp': account.exp,
            'mileage': account.mileage,
        }
    else: # 사용자 정보가 없는 경우
        return {
            'id': '',
            'account_type': 'guest',
            'level': {
                'level': 0
            }
        }

# 사용자 상세 정보 가져오기(모든 정보)
def select_account_detail(account_id):

    # 사용자 정보 확인
    account = models.ACCOUNT.objects.filter(
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
            'tel': account.tel,
            'account_type': account.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
            'status': account.status,
            'subsupervisor_permissions': str(account.subsupervisor_permissions).split(','),
            'level': select_level(account.level.pk),
            'bookmarked_posts': [post.id for post in account.bookmarked_posts.all()],
            'exp': account.exp,
            'mileage': account.mileage,
            'note': account.note,
            'created_at': datetime.datetime.strftime(account.date_joined, '%Y-%m-%d %H:%M'),
            'last_login': datetime.datetime.strftime(account.last_login, '%Y-%m-%d %H:%M') if account.last_login else None,
        }
    else: # 사용자 정보가 없는 경우
        return {
            'id': '',
            'account_type': 'guest',
            'level': {
                'level': 0
            }
        }

# 사용자 검색
def select_accounts(nickname=None, username=None, any=None, account_type=None, status=None, page=1):

    # 사용자 정보 확인
    accounts = models.ACCOUNT.objects
    query = Q()
    if nickname: # 닉네임 검색
        query &= Q(first_name=nickname)
    if username: # 아이디 검색(로그인용 아이디)
        query &= Q(username=username)
    if any: # 아이디 또는 닉네임 검색
        query &= Q(first_name=any) | Q(username=any)
    if status:  # 상태 검색
        query &= Q(status=status)
    if account_type: # 계정 타입 검색
        query &= Q(groups__name__in=[account_type])
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
        'account_type': [group.name for group in account.groups.all()],
        'status': account.status,
        'subsupervisor_permissions': str(account.subsupervisor_permissions).split(','),
        'level': select_level(account.level.pk),
        'exp': account.exp,
        'mileage': account.mileage,
    } for account in accounts]

    return accounts_data, last_page

# 사용자 생성
def create_account(username, password, nickname, account_type, partner_name=None, email=None, tel=None):

    # 사용자 정보 확인(중복 확인)
    exist = models.ACCOUNT.objects.filter(
        Q(username=username) | Q(first_name=nickname) # 아이디 또는 닉네임 중복 확인
    ).exists()
    if exist:
        return {
            'success': False,
            'message': '이미 존재하는 사용자입니다.',
        }

    # 사용자 생성
    account = models.ACCOUNT.objects.create(
        username=username,
        first_name=nickname,
    )
    account.set_password(password)
    account.save()
    if email:
        account.email = email
    if tel:
        account.tel = tel
    if partner_name:
        account.last_name = partner_name
    if account_type == 'user': # 사용자
        account.groups.add(Group.objects.get(name='user'))
        account.status = 'active'
    elif account_type == 'partner': # 파트너(pending)
        account.groups.add(Group.objects.get(name='partner'))
        account.status = 'pending'
    elif account_type == 'dame': # 여성 회원(pending)
        account.groups.add(Group.objects.get(name='dame'))
        account.status = 'pending'
    elif account_type == 'subsupervisor': # 부관리자
        account.groups.add(Group.objects.get(name='subsupervisor'))
        account.status = 'active'
    account.level = models.LEVEL_RULE.objects.get(level=1)
    account.save()

    return {
        'success': True,
        'message': '사용자가 생성되었습니다.',
        'pk': account.id,
        'status': account.status,
    }

# 사용자 정보 업데이트
def update_account(account_id, password=None, nickname=None, partner_name=None, email=None, tel=None, status=None, note=None, subsupervisor_permissions=None, exp=None, mileage=None, recent_ip=None):

    # 사용자 정보 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    ).first()
    if not account:
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 사용자 정보 업데이트
    if password: # 비밀번호 업데이트
        account.set_password(password)
    if nickname: # 닉네임 업데이트
        account.first_name = nickname
    if partner_name: # 파트너 이름 업데이트
        account.last_name = partner_name
    if email: # 이메일 업데이트
        account.email = email
    if tel: # 전화번호 업데이트
        account.tel = tel
    if status: # 상태 업데이트
        account.status = status
    if note: # 메모 업데이트
        account.note = note
    if subsupervisor_permissions: # 부관리자 권한 업데이트
        account.subsupervisor_permissions = subsupervisor_permissions
    if recent_ip: # 최근 접속 IP 업데이트
        account.recent_ip = recent_ip
    if exp: # 경험치 업데이트
        account.exp = exp

        # 레벨업 확인
        level = models.LEVEL_RULE.objects.filter(
            required_exp__lte=exp
        ).order_by('-level').first()
        if level and level.level > account.level.level:
            account.level = level

            # 레벨업 활동 생성
            create_account_activity(
                account_id=account_id,
                message=f'[레벨업] {level.text} 레벨을 달성하였습니다.'
            )

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
    accounts = models.ACCOUNT.objects.select_related('level').prefetch_related('groups')
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
        query &= Q(groups__name__in=[account_type])

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
        'account_type': [group.name for group in account.groups.all()],
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
    ).order_by('-created_at')

    # 페이지네이션
    last_page = (activities.count() // 20) + 1
    activities = activities[(page-1)*20:page*20]

    # 사용자 활동 내역 포멧
    activities_data = [{
        'id': activity.id,
        'message': activity.message,
        'exp_change': activity.exp_change,
        'mileage_change': activity.mileage_change,
        'created_at': datetime.datetime.strftime(activity.created_at, '%Y-%m-%d %H:%M'),
    } for activity in activities]

    return activities_data, last_page

# 사용자 활동 생성
def create_account_activity(account_id, message, exp_change=0, mileage_change=0):

    if account_id in ['guest', 'supervisor']:
        return

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
            'image': '/media/' + str(level.image) if level.image else None,
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
        'image': '/media/' + str(level.image) if level.image else None,
        'text': level.text,
        'text_color': level.text_color,
        'background_color': level.background_color,
        'required_exp': level.required_exp,
    } for level in levels]

    return levels_data

# 레벨 생성
def create_level(image, text, text_color, background_color, required_exp):

    # 레벨 생성
    level = models.LEVEL_RULE.objects.create(
        image=image,
        text=text,
        text_color=text_color,
        background_color=background_color,
        required_exp=required_exp,
    )

    return {
        'success': True,
        'message': '레벨이 생성되었습니다.',
        'pk': level.level,
    }

# 레벨 정보 업데이트
def update_level(level, image=None, text=None, text_color=None, background_color=None, required_exp=None):

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
    if required_exp: # 필요 경험치 업데이트
        level.required_exp = required_exp
    level.save()

    return {
        'success': True,
        'message': '레벨 정보가 업데이트 되었습니다.',
        'pk': level.level,
    }



##### [POST & PLACE_INFO]
# 게시글 검색
def select_posts(title=None, category_id=None, board_id=None, related_post_id=None, order='default', page=1, post_type='default'):

    # 게시글 정보 확인
    posts = models.POST.objects.exclude(
        author__isnull=True
    ).select_related(
        'author', 'related_post', 'place_info'
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
    if post_type == 'travel': # place_info가 None이 아닌지 확인
        query &= Q(place_info__isnull=False)
        query &= Q(place_info__status__in=['ad', 'active', 'pending'])
    elif post_type == 'ad': # place_info의 status가 'ad'인지 확인
        query &= Q(place_info__status='ad')

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
            'id': post.author.id,
            'nickname': post.author.first_name,
            'partner_name': post.author.last_name,
            'level': select_level(post.author.level.level),
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
            'location_info': post.place_info.location_info if len(post.place_info.location_info) <= 16 else post.place_info.location_info[:20] + '..',
            'open_info': post.place_info.open_info if len(post.place_info.open_info) <= 16 else post.place_info.open_info[:20] + '..',
            'status': post.place_info.status,
        } if post.place_info else None,
        'boards': [{
            'id': board.id,
            'name': board.name,
        } for board in post.boards.all()],
        'board_ids': [board.id for board in post.boards.all()],
        'title': post.title,
        'image': '/media/' + str(post.image) if post.image else None,
        'view_count': post.view_count,
        'like_count': post.like_count,
        'created_at': datetime.datetime.strftime(post.created_at, '%Y-%m-%d %H:%M'),
        'comment_count': models.COMMENT.objects.filter(post=post).count(),
    } for post in posts]

    return posts_data, last_page

# 사용자 북마크한 게시글 가져오기
def select_account_bookmarked_posts(account_id):

    # 사용자 확인
    account = models.ACCOUNT.objects.prefetch_related(
        'bookmarked_posts'
    ).prefetch_related(
        'bookmarked_posts__author', 'bookmarked_posts__related_post', 'bookmarked_posts__place_info', 'bookmarked_posts__boards', 'bookmarked_posts__place_info__categories'
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
        'image': '/media/' + str(post.image) if post.image else None,
        'view_count': post.view_count,
        'like_count': post.like_count,
        'created_at': datetime.datetime.strftime(post.created_at, '%Y-%m-%d %H:%M'),
        'comment_count': models.COMMENT.objects.filter(post=post).count(),
    } for post in posts]

    return posts_data

# 게시글 정보 가져오기
def select_post(post_id=None, title=None):

    # 게시글 정보 확인
    query = Q()
    if title:
        query &= Q(title=title)
    if post_id:
        query &= Q(id=post_id)

    post = models.POST.objects.select_related(
        'author', 'related_post', 'place_info'
    ).prefetch_related(
        'include_coupons', 'boards', 'place_info__categories', 'boards__comment_groups', 'include_coupons__related_post'
    ).filter(
        query
    ).first()
    if not post:
        return {
            'success': False,
            'message': '게시글 정보가 존재하지 않습니다.',
        }

    # 포함된 쿠폰
    include_coupons = []
    for coupon in post.include_coupons.all():
        if coupon.status != 'active':
            continue
        include_coupons.append({
            'name': coupon.name,
            'expire_at': datetime.datetime.strftime(coupon.expire_at, '%Y-%m-%d'),
            'required_mileage': coupon.required_mileage,
            'related_post': {
                'id': coupon.related_post.id,
                'title': coupon.related_post.title,
                'board_ids': ''.join([str(board.id) for board in coupon.related_post.boards.all()]),
            } if coupon.related_post else None,
        })

    # 게시글 정보 포멧
    post_data = {
        'id': post.id,
        'author': {
            'id': post.author.id,
            'nickname': post.author.first_name,
            'partner_name': post.author.last_name,
            'account_type': post.author.groups.all()[0].name,
            'level': select_level(post.author.level.level),
        },
        'related_post': {
            'id': post.related_post.id,
            'title': post.related_post.title,
        } if post.related_post else None,
        'place_info': {
            'id': post.place_info.id,
            'categories': [{
                'id': c.id,
                'name': c.name,
            } for c in post.place_info.categories.all()],
            'category_ids': [c.id for c in post.place_info.categories.all()],
            'location_info': post.place_info.location_info,
            'open_info': post.place_info.open_info,
            'status': post.place_info.status,
            'address': post.place_info.address,
        } if post.place_info else None,
        'boards': [{
            'id': board.id,
            'name': board.name,
            'board_type': board.board_type,
            'comment_groups': [group.name for group in board.comment_groups.all()],
            'level_cut': board.level_cut,
        } for board in post.boards.all()],
        'board_ids': [board.id for board in post.boards.all()],
        'include_coupons': include_coupons,
        'title': post.title,
        'content': post.content,
        'image': '/media/' + str(post.image) if post.image else None,
        'view_count': post.view_count,
        'like_count': post.like_count,
        'created_at': datetime.datetime.strftime(post.created_at, '%Y-%m-%d %H:%M'),
        'search_weight': post.search_weight,
        'comment_count': models.COMMENT.objects.filter(post=post).count(),
    }

    return post_data

# 게시글 생성
def create_post(title, content, board_ids, author_id=None, related_post_id=None, image=None, include_coupon_name=None):

    # 사용자 확인
    account = models.ACCOUNT.objects.filter(
        id=author_id
    ).first()

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
        author=account,
        related_post=related_post.first() if related_post_id else None,
        title=title,
        content=content,
        image=image,
    )
    if include_coupon_name:
        coupons = models.COUPON.objects.filter(
            name=include_coupon_name
        )
        post.include_coupons.set(coupons)
    post.boards.set(boards)
    post.save()

    return {
        'success': True,
        'message': '게시글이 생성되었습니다.',
        'pk': post.id,
    }

# 게시글의 여행지 정보 생성
def create_post_place_info(post_id, category_ids, location_info, open_info, status, address):

    # 게시글 확인
    post = models.POST.objects.filter(
        id=post_id
    )
    if not post.exists():
        return {
            'success': False,
            'message': '게시글 정보가 존재하지 않습니다.',
        }

    # 게시글의 여행지 정보 생성
    place_info = models.PLACE_INFO.objects.create(
        post=post.first(),
        location_info=location_info,
        open_info=open_info,
        status=status,
        address=address,
    )
    for category_id in str(category_ids).split(','):
        category = models.CATEGORY.objects.filter(
            id=category_id
        ).first()
        if category:
            place_info.categories.add(category)
    place_info.save()

    return {
        'success': True,
        'message': '게시글의 여행지 정보가 생성되었습니다.',
        'pk': place_info.id,
    }

# 게시글 정보 업데이트
def update_post(post_id, title=None, content=None, image=None, board_ids=None, search_weight=None, view_count=None, like_count=None, place_info_id=None):

    # 게시글 확인
    post = models.POST.objects.filter(
        id=post_id
    )
    if not post.exists():
        return {
            'success': False,
            'message': '게시글 정보가 존재하지 않습니다.',
        }

    # 게시글 정보 업데이트
    post = post.first()
    if title: # 제목 업데이트
        post.title = title
    if content: # 내용 업데이트
        post.content = content
    if image: # 이미지 업데이트
        post.image = image
    if board_ids: # 게시판 업데이트
        post.boards.clear()
        for board_id in str(board_ids).split(','):
            board = models.BOARD.objects.filter(
                id=board_id
            ).first()
            if board:
                post.boards.add(board)
    if search_weight: # 검색 가중치 업데이트
        post.search_weight = search_weight
    if view_count: # 조회수 업데이트
        post.view_count = view_count
    if like_count: # 좋아요 수 업데이트
        post.like_count = like_count
    if place_info_id:
        place_info = models.PLACE_INFO.objects.filter(
            id=place_info_id
        ).first()
        if place_info:
            post.place_info = place_info
    post.save()

    return {
        'success': True,
        'message': '게시글 정보가 업데이트 되었습니다.',
        'pk': post.id,
    }

# 게시글의 여행지 정보 업데이트
def update_place_info(post_id, category_ids=None, location_info=None, open_info=None, status=None, ad_start_at=None, ad_end_at=None, note=None, address=None):

    # 게시글 확인
    post = models.POST.objects.filter(
        id=post_id
    ).first()
    if not post:
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
            ).first()
            if not category:
                return {
                    'success': False,
                    'message': '카테고리 정보가 존재하지 않습니다.',
                }
            else:
                categories.append(category)

    # 게시글의 여행지 정보 확인
    place_info = models.PLACE_INFO.objects.filter(
        post=post
    ).first()
    if not place_info:
        return {
            'success': False,
            'message': '게시글의 여행지 정보가 존재하지 않습니다.',
        }

    # 게시글의 여행지 정보 업데이트
    if categories: # 카테고리 업데이트
        place_info.categories.clear()
        for category_id in str(category_ids).split(','):
            category = models.CATEGORY.objects.filter(
                id=category_id
            ).first()
            if category:
                place_info.categories.add(category)
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
    if address:
        place_info.address = address
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

# 게시글의 여행지 정보 삭제
def delete_place_info(place_info_id):

    # 게시글의 여행지 정보 삭제
    place_info = models.PLACE_INFO.objects.filter(
        id=place_info_id
    ).first()
    place_info.delete()

    return {
        'success': True,
        'message': '게시글의 여행지 정보가 삭제되었습니다.',
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
    comments_data = []

    for comment in comments:
        subcomments = models.COMMENT.objects.select_related(
            'author'
        ).filter(
            parent_comment=comment
        )

        comments_data.append({
            'id': comment.id,
            'author': {
                'id': comment.author.id,
                'nickname': comment.author.first_name,
                'partner_name': comment.author.last_name,
                'level': select_level(comment.author.level.pk),
            },
            'content': comment.content,
            'hide': comment.hide,
            'created_at': datetime.datetime.strftime(comment.created_at, '%Y-%m-%d %H:%M'),
            'subcomments': [{
                'id': subcomment.id,
                'author': {
                    'id': subcomment.author.id,
                    'nickname': subcomment.author.first_name,
                    'partner_name': subcomment.author.last_name,
                    'level': select_level(subcomment.author.level.pk),
                },
                'content': subcomment.content,
                'hide': subcomment.hide,
                'created_at': datetime.datetime.strftime(subcomment.created_at, '%Y-%m-%d %H:%M'),
            } for subcomment in subcomments],
        })

    return comments_data

# 댓글 생성
def create_comment(content, account_id, post_id=None, parent_comment_id=None, hide=False):

    # 게시글 확인
    post = models.POST.objects.filter(
        id=post_id
    ).first()

    # 사용자 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    ).first()
    if not account:
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 부모 댓글 확인
    parent_comment_author_id = None
    if parent_comment_id:
        parent_comment = models.COMMENT.objects.filter(
            id=parent_comment_id
        ).first()
        if not parent_comment:
            return {
                'success': False,
                'message': '부모 댓글 정보가 존재하지 않습니다.',
            }
        parent_comment_author_id = parent_comment.author.id

    # 댓글 생성
    comment = models.COMMENT.objects.create(
        post=post,
        author=account,
        content=content,
        hide=hide,
    )
    if parent_comment_id:
        comment.parent_comment = parent_comment
    comment.save()

    # 대댓글 작성
    if parent_comment_id:
        point = int(select_server_setting('comment_point'))
        account.mileage += point
        account.exp += point
        account.save()

        return {
            'success': True,
            'message': '댓글이 생성되었습니다.',
            'type': 'comment',
            'point': point,
            'pk': comment.id,
            'parent_comment_author_id': parent_comment_author_id,
        }

    # 출석체크, 가입 인사 확인 및 포인트 지급
    if post.title.startswith('attendance:'):
        point = int(select_server_setting('attend_point'))
        account.mileage += point
        account.exp += point
        account.save()

        return {
            'success': True,
            'message': '출석체크가 완료되었습니다.',
            'type': 'attendance',
            'point': point,
            'pk': comment.id,
        }
    elif post.title.startswith('greeting:'):
        point = int(select_server_setting('comment_point'))
        account.mileage += point
        account.exp += point
        account.save()

        return {
            'success': True,
            'message': '가입 인사가 완료되었습니다.',
            'type': 'greeting',
            'pk': comment.id,
        }
    elif post.title.startswith('talk:'):
        point = int(select_server_setting('comment_point'))
        account.mileage += point
        account.exp += point
        account.save()

        return {
            'success': True,
            'message': '대화가 생성되었습니다.',
            'type': 'talk',
            'point': point,
            'pk': comment.id,
        }

    point = int(select_server_setting('comment_point'))
    account.mileage += point
    account.exp += point
    account.save()

    return {
        'success': True,
        'message': '댓글이 생성되었습니다.',
        'type': 'comment',
        'point': point,
        'pk': comment.id,
        'parent_comment_author_id': parent_comment_author_id,
    }

# 댓글 업데이트
def update_comment(comment_id, content=None, hide=None):

    # 댓글 확인
    comment = models.COMMENT.objects.filter(
        id=comment_id
    ).first()
    if not comment:
        return {
            'success': False,
            'message': '댓글 정보가 존재하지 않습니다.',
        }

    # 댓글 업데이트
    if content:
        comment.content = content
    if hide != None:
        comment.hide = hide
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
def select_coupons(code=None, name=None, status=None, create_account_id=None, own_account_id=None, page=1):

    # 모든 쿠폰 정보 확인
    coupons = models.COUPON.objects.select_related(
        'own_account', 'related_post', 'create_account', 'own_account__level',
    ).prefetch_related(
        'create_account__groups'
    )

    query = Q()
    if code:
        query &= Q(code=code)
    if name:
        query &= Q(name__icontains=name)
    if status and status != 'history':
        query &= Q(status=status)
    elif status == 'history':
        query &= Q(status__in=['used', 'expired', 'deleted'])
    if create_account_id:
        query &= Q(create_account__id=create_account_id)
    if own_account_id:
        query &= Q(own_account__id=own_account_id)

    coupons = coupons.filter(query).order_by('-created_at')

    # 페이지네이션
    last_page = (coupons.count() // 20) + 1
    coupons = coupons[(page-1)*20:page]

    # 쿠폰 정보 포멧
    coupons_data = [{
        'code': coupon.code,
        'related_post': {
            'id': coupon.related_post.id,
            'title': coupon.related_post.title,
        } if coupon.related_post else None,
        'name': coupon.name,
        'content': coupon.content,
        'image': '/media/' + str(coupon.image) if coupon.image else None,
        'expire_at': datetime.datetime.strftime(coupon.expire_at, '%Y-%m-%d'),
        'required_mileage': coupon.required_mileage,
        'own_account': {
            'id': coupon.own_account.id,
            'nickname': coupon.own_account.first_name,
            'level': select_level(coupon.own_account.level.level),
        } if coupon.own_account else None,
        'create_account': {
            'id': coupon.create_account.id,
            'nickname': coupon.create_account.first_name,
            'partner_name': coupon.create_account.last_name,
            'account_type': coupon.create_account.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
        } if coupon.create_account else None,
        'status': coupon.status,
        'note': coupon.note,
    } for coupon in coupons]

    return coupons_data, last_page

# 쿠폰 정보 가져오기
def select_coupon(code):

    # 쿠폰 정보 확인
    coupon = models.COUPON.objects.select_related(
        'own_account', 'related_post', 'create_account', 'own_account__level',
    ).prefetch_related(
        'create_account__groups'
    ).filter(
        code=code
    ).first()
    if not coupon:
        return {
            'success': False,
            'message': '쿠폰 정보가 존재하지 않습니다.',
        }

    # 쿠폰 정보 포멧
    coupon_data = {
        'code': coupon.code,
        'required_mileage': coupon.required_mileage,
        'own_account': {
            'id': coupon.own_account.id,
        } if coupon.own_account else None,
        'create_account': {
            'id': coupon.create_account.id,
        } if coupon.create_account else None,
        'status': coupon.status,
    }

    return coupon_data

# 쿠폰 생성
def create_coupon(account_id, code, related_post_id, name, content, image, expire_at, required_mileage):

    # 사용자 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    ).first()
    if not account:
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # related_post 확인
    related_post = models.POST.objects.filter(
        id=related_post_id
    ).first()
    if not related_post:
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
        related_post=related_post,
        name=name,
        content=content,
        image=image,
        expire_at=expire_at,
        required_mileage=required_mileage,
        create_account=account,
    )

    return {
        'success': True,
        'message': '쿠폰이 생성되었습니다.',
        'pk': coupon.code,
    }

# 쿠폰 정보 업데이트
def update_coupon(code, name=None, content=None, image=None, expire_at=None, required_mileage=None, own_account_id=None, status=None, note=None, related_post_id=None):

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
    if own_account_id != '' and own_account_id:
        own_account = models.ACCOUNT.objects.filter(
            id=own_account_id
        ).first()
        if not own_account:
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
        coupon.own_account = own_account
    if own_account_id == '': # 소유자 삭제
        coupon.own_account = None
    if status: # 상태 업데이트
        coupon.status = status
    if note: # 메모 업데이트
        coupon.note = note
    if related_post_id:
        post = models.POST.objects.filter(
            id=related_post_id
        ).first()
        if post:
            coupon.related_post = post
    coupon.save()

    return {
        'success': True,
        'message': '쿠폰 정보가 업데이트 되었습니다.',
        'pk': coupon.code,
    }



##### [MESSAGE]
# 메세지 가져오기
def select_message(message_id):

    # 메세지 확인
    message = models.MESSAGE.objects.select_related(
        'include_coupon', 'sender_account', 'receive_account'
    ).filter(
        id=message_id
    ).first()
    if not message:
        return {
            'success': False,
            'message': '메세지 정보가 존재하지 않습니다.',
        }

    # 보낸 사람 정보
    if not message.sender: # 관리자
        sender_account = {
            'id': '',
            'nickname': '관리자',
            'account_type': 'supervisor',
        }
    else:
        sender_account = {
            'id': message.sender_account.id,
            'nickname': message.sender_account.first_name,
            'partner_name': message.sender_account.last_name,
            'account_type': message.sender_account.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
            'level': select_level(message.sender_account.level.level),
        }

    # 받는 사람 정보
    if message.receive == '': # 관리자
        receive_account = {
            'id': '',
            'nickname': '관리자',
            'account_type': 'supervisor',
        }
    else:
        receive_account = {
            'id': message.receive_account.id,
            'nickname': message.receive_account.first_name,
            'partner_name': message.receive_account.last_name,
            'account_type': message.receive_account.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
            'level': select_level(message.receive_account.level.level),
        }

    # 메세지 정보 포멧
    message_data = {
        'id': message.id,
        'sender_account': sender_account,
        'receive_account': receive_account,
        'title': message.title,
        'content': message.content,
        'image': '/media/' + str(message.image) if message.image else None,
        'include_coupon': {
            'code': message.include_coupon.code,
            'name': message.include_coupon.name,
            'required_mileage': message.include_coupon.required_mileage,
            'expire_at': datetime.datetime.strftime(message.include_coupon.expire_at, '%Y-%m-%d'),
        } if message.include_coupon else None,
        'is_read': message.is_read,
        'created_at': datetime.datetime.strftime(message.created_at, '%Y-%m-%d %H:%M'),
    }

    return message_data

# 메세지 검색
def select_messages(receive_account_id=None, send_account_id=None, is_read=None, message_type=None, page=1):

    # 메세지 확인
    msgs = models.MESSAGE.objects.select_related(
        'include_coupon' , 'sender', 'receive'
    ).order_by('-created_at')

    # 쿼리 필터
    query = Q()
    if receive_account_id:
        query &= Q(receive__id=receive_account_id)
    else:
        query &= Q(receive__isnull=True)
    if send_account_id:
        query &= Q(sender__id=send_account_id)
    else:
        query &= Q(sender__isnull=True)
    if is_read:
        query &= Q(is_read=is_read)
    if message_type:
        query &= Q(message_type=message_type)
    msgs = msgs.filter(query)

    # 페이지네이션
    last_page = (msgs.count() // 20) + 1
    msgs = msgs[(page-1)*20:page*20]
    messages = []

    # 메세지 정보 포멧
    for msg in msgs:

        # 보낸 사람 정보
        if not msg.sender: # supervisor
            sender_account = {
                'id': 'supervisor',
                'nickname': '관리자',
                'account_type': 'supervisor',
            }
        else:
            sender_account = {
                'id': msg.sender.id,
                'nickname': msg.sender.first_name,
                'partner_name': msg.sender.last_name,
                'account_type': msg.sender.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
                'level': select_level(msg.sender.level.level),
            }

        # 받는 사람 정보
        if not msg.receive:
            receive_account = {
                'id': '',
                'nickname': '관리자',
                'account_type': 'supervisor',
            }
        else:
            receive_account = {
                'id': msg.receive.id,
                'nickname': msg.receive.first_name,
                'partner_name': msg.receive.last_name,
                'account_type': msg.receive.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
                'level': select_level(msg.receive.level.level),
            }

        # 메세지 포멧
        messages.append({
            'id': msg.id,
            'sender_account': sender_account,
            'receive_account': receive_account,
            'title': msg.title,
            'content': msg.content,
            'image': '/media/' + str(msg.image) if msg.image else None,
            'include_coupon': {
                'code': msg.include_coupon.code,
                'name': msg.include_coupon.name,
                'required_mileage': msg.include_coupon.required_mileage,
                'expire_at': datetime.datetime.strftime(msg.include_coupon.expire_at, '%Y-%m-%d'),
            } if msg.include_coupon else None,
            'is_read': msg.is_read,
            'created_at': datetime.datetime.strftime(msg.created_at, '%Y-%m-%d %H:%M'),
        })

    return messages, last_page

# 메세지 생성
def create_message(title, content, message_type, receive_account_id=None, sender_account_id=None, image=None, include_coupon_code=None):

    # 보낸 사람 확인
    if sender_account_id:
        sender_id = models.ACCOUNT.objects.filter(
            id=sender_account_id
        ).first()

    # 받는 사람 확인
    if receive_account_id and receive_account_id != 'all':
        receiver_id = models.ACCOUNT.objects.filter(
            id=receive_account_id
        ).first()
    elif receive_account_id == 'all':
        receiver_id = 'all'
    else:
        receiver_id = None

    # 쿠폰 확인
    if include_coupon_code:
        coupon = models.COUPON.objects.filter(
            code=include_coupon_code
        ).first()

    # 메세지 생성
    if receiver_id != 'all':
        message = models.MESSAGE.objects.create(
            title=title,
            content=content,
            message_type=message_type,
        )
        if sender_account_id:
            message.sender = sender_id # 보낸 사람, 없으면 관리자
        if receive_account_id:
            message.receive = receiver_id # 받는 사람, 없으면 관리자
        if image:
            message.image = image # 이미지
        if include_coupon_code:
            message.include_coupon = coupon # 쿠폰
        message.save()
    else: # 모든 사용자에게(관리자만 가능)
        accounts = models.ACCOUNT.objects.all()
        for account in accounts:
            message = models.MESSAGE.objects.create(
                receive=account,
                title=title,
                content=content,
                message_type=message_type,
            )

    return {
        'success': True,
        'message': '메세지가 생성되었습니다.',
        'pk': message.id,
    }

# 메세지 정보 업데이트(읽음 처리 및 쿠폰 삭제)
def update_message(message_id, delete_coupon=False):

    # 메세지 확인
    message = models.MESSAGE.objects.filter(
        id=message_id
    ).first()
    if not message:
        return {
            'success': False,
            'message': '메세지 정보가 존재하지 않습니다.',
        }

    # 메세지 업데이트
    message.is_read = True
    if delete_coupon:
        message.include_coupon = None
    message.save()

    return {
        'success': True,
        'message': '메세지가 읽음 처리 되었습니다.',
        'pk': message.id,
    }



##### [SERVER_SETTING & UPLOAD]
# 모든 서버 설정 가져오기
def select_server_settings():

    # 모든 서버 설정 확인
    server_settings = models.SERVER_SETTING.objects.all()

    # 서버 설정 포멧(리스트를 딕셔너리로 변환)
    server_settings_data = {}
    for server_setting in server_settings:
        server_settings_data[server_setting.name] = server_setting.value

    return server_settings_data

# 서버 설정 가져오기
def select_server_setting(name):

    # 서버 설정 확인
    server_setting = models.SERVER_SETTING.objects.filter(
        name=name
    )

    return server_setting.first().value

# 서버 설정 업데이트
def update_server_setting(name, value):

    # 서버 설정 확인
    server_setting = models.SERVER_SETTING.objects.filter(
        name=name
    )

    # 서버 설정 업데이트
    server_setting = server_setting.first()
    server_setting.value = value
    server_setting.save()

    return {
        'success': True,
        'message': '서버 설정이 업데이트 되었습니다.',
        'pk': server_setting.name,
    }

# 파일 업로드 및 경로 반환
def upload_file(file):

    # 파일 업로드
    upload = models.UPLOAD.objects.create(
        file=file
    )

    return {
        'success': True,
        'message': '파일이 업로드 되었습니다.',
        'path': upload.file.url,
    }



##### [BANNER]
# 배너 정보 가져오기
def select_banners(location):

    # 모든 배너 정보 확인
    bs = models.BANNER.objects.filter(
        location=location
    ).order_by('display_weight')

    # 배너 정보 포멧
    banners = []
    for banner in bs:
        banners.append({
            'id': banner.id,
            'location': banner.location,
            'image': '/media/' + str(banner.image),
            'link': banner.link,
            'status': banner.status,
            'display_weight': banner.display_weight,
        })

    return banners

# 배너 생성
def create_banner(location, image, link, status, display_weight):

    # 배너 생성
    banner = models.BANNER.objects.create(
        location=location,
        image=image,
        link=link,
        status=status,
        display_weight=display_weight,
    )

    return {
        'success': True,
        'message': '배너가 생성되었습니다.',
        'pk': banner.id,
    }

# 배너 정보 업데이트
def update_banner(banner_id, location=None, image=None, link=None, status=None, display_weight=None):

    # 배너 확인
    banner = models.BANNER.objects.filter(
        id=banner_id
    ).first()
    if not banner:
        return {
            'success': False,
            'message': '배너 정보가 존재하지 않습니다.',
        }

    # 배너 정보 업데이트
    if location:
        banner.location = location
    if image:
        banner.image = image
    if link:
        banner.link = link
    if status:
        banner.status = status
    if display_weight:
        banner.display_weight = display_weight
    banner.save()

    return {
        'success': True,
        'message': '배너 정보가 업데이트 되었습니다.',
        'pk': banner.id,
    }

# 배너 삭제
def delete_banner(banner_id):

    # 배너 삭제
    banner = models.BANNER.objects.filter(
        id=banner_id
    ).first()
    banner.delete()

    return {
        'success': True,
        'message': '배너가 삭제되었습니다.',
    }



##### [STATISTIC]
# 통계 정보 가져오기
def select_all_statistics(days_ago=7):

    # 통계 정보 확인
    now = datetime.datetime.now()
    statistics = models.STATISTIC.objects.filter(
        date__gte=now - datetime.timedelta(days=days_ago)
    )

    # 통계 정보 포멧
    statistics_data = []
    for statistic in statistics:
        statistics_data.append({
            'name': statistic.name,
            'value': statistic.value,
            'date': datetime.datetime.strftime(statistic.date, '%Y-%m-%d'),
        })

    return statistics_data

# 통계 생성
def create_statistic(name):

    # 통계 생성
    exist = models.STATISTIC.objects.filter(
        name=name,
        date=datetime.datetime.now()
    ).first()
    if exist:
        exist.value += 1
        exist.save()
    else:
        models.STATISTIC.objects.create(
            name=name,
            value=1
        )

    return {
        'success': True,
        'message': '통계가 생성되었습니다.',
    }



##### [Blocked_IP]
# 차단된 IP 정보 가져오기
def select_blocked_ips():

    # 차단된 IP 정보 확인
    blocked_ips = models.BLOCKED_IP.objects.all()

    # 차단된 IP 정보 포멧
    blocked_ips_data = []
    for blocked_ip in blocked_ips:
        blocked_ips_data.append(blocked_ip.ip)

    return blocked_ips_data

# IP 차단
def create_blocked_ip(ip):

    # 이미 차단된 IP인지 확인
    exist = models.BLOCKED_IP.objects.filter(
        ip=ip
    ).exists()
    if exist:
        return {
            'success': False,
            'message': '이미 차단된 IP입니다.',
        }

    # IP 차단
    models.BLOCKED_IP.objects.create(
        ip=ip
    )

    return {
        'success': True,
        'message': 'IP가 차단되었습니다.',
    }

# IP 차단 해제
def delete_blocked_ip(ip):

    # 차단된 IP 확인
    blocked_ip = models.BLOCKED_IP.objects.filter(
        ip=ip
    )
    if not blocked_ip.exists():
        return {
            'success': False,
            'message': '차단된 IP 정보가 존재하지 않습니다.',
        }

    # IP 차단 해제
    blocked_ip.first().delete()

    return {
        'success': True,
        'message': 'IP 차단이 해제되었습니다.',
    }



##### [BOARD & CATEGORY TREE]
# 게시판 트리 생성
def make_board_tree(board_type=None, status=False):

    # 게시판 확인
    query = Q()
    if board_type != 'not_travel' and board_type:
        query &= Q(board_type=board_type)
    elif board_type == 'not_travel':
        query &= ~Q(board_type='travel')
    boards = models.BOARD.objects.prefetch_related(
        'display_groups', 'write_groups', 'comment_groups'
    ).filter(query).order_by('-display_weight')

    # 부모 게시판이 없는 게시판(최상위 게시판)을 먼저 생성
    board_dict = {
        board.name: {
            'id': board.id,
            'name': board.name,
            'level_cut': board.level_cut,
            'board_type': board.board_type,
            'display_groups': [group.name for group in board.display_groups.all()],
            'write_groups': [group.name for group in board.write_groups.all()],
            'comment_groups': [group.name for group in board.comment_groups.all()],
            'display_weight': board.display_weight,
            'total_views': int(math.fsum([post.view_count for post in models.POST.objects.filter(Q(boards__id__in=str(board.id)))])) if status else 0,
            'total_posts': models.POST.objects.filter(Q(boards__id__in=str(board.id))).count() if status else 0,
            'children': [],
        } for board in boards if not board.parent_board
    }

    # 하위 게시판 생성
    for board in boards:
        if board.parent_board: # 부모 게시판이 존재할 경우,
            if board_dict.get(board.parent_board.name): # 부모 게시판의 자식으로 추가
                children = {
                    'id': board.id,
                    'name': board.name,
                    'level_cut': board.level_cut,
                    'board_type': board.board_type,
                    'display_groups': [group.name for group in board.display_groups.all()],
                    'write_groups': [group.name for group in board.write_groups.all()],
                    'comment_groups': [group.name for group in board.comment_groups.all()],
                    'display_weight': board.display_weight,
                    'total_views': int(math.fsum([post.view_count for post in models.POST.objects.filter(Q(boards__id__in=str(board.id)))])) if status else 0,
                    'total_posts': models.POST.objects.filter(Q(boards__id__in=str(board.id))).count() if status else 0,
                    'children': [],
                }
                #if children not in board_dict[board.parent_board.name]['children']:
                board_dict[board.parent_board.name]['children'].append(children)
            else: # 부모 게시판이 없을 경우, 3차 이상의 노드들
                loop = True
                for key in board_dict.keys(): # 부모 게시판의 자식의 자식 확인...
                    for child in board_dict[key]['children']:
                        if not loop:
                            break
                        if child['name'] == board.parent_board.name:
                            children = {
                                'id': board.id,
                                'name': board.name,
                                'level_cut': board.level_cut,
                                'board_type': board.board_type,
                                'display_groups': [group.name for group in board.display_groups.all()],
                                'write_groups': [group.name for group in board.write_groups.all()],
                                'comment_groups': [group.name for group in board.comment_groups.all()],
                                'display_weight': board.display_weight,
                                'total_views': int(math.fsum([post.view_count for post in models.POST.objects.filter(Q(boards__id__in=str(board.id)))])) if status else 0,
                                'total_posts': models.POST.objects.filter(Q(boards__id__in=str(board.id))).count() if status else 0,
                                'children': [],
                            }
                            #if children not in child['children']:
                            child['children'].append(children)
                            loop = False
                        if loop:
                            for grandchild in child['children']:
                                if not loop:
                                    break
                                if grandchild['name'] == board.parent_board.name:
                                    children = {
                                        'id': board.id,
                                        'name': board.name,
                                        'level_cut': board.level_cut,
                                        'board_type': board.board_type,
                                        'display_groups': [group.name for group in board.display_groups.all()],
                                        'write_groups': [group.name for group in board.write_groups.all()],
                                        'comment_groups': [group.name for group in board.comment_groups.all()],
                                        'display_weight': board.display_weight,
                                        'total_views': int(math.fsum([post.view_count for post in models.POST.objects.filter(Q(boards__id__in=str(board.id)))])) if status else 0,
                                        'total_posts': models.POST.objects.filter(Q(boards__id__in=str(board.id))).count() if status else 0,
                                        'children': [],
                                    }
                                    # if children not in grandchild['children']:
                                    grandchild['children'].append(children)
                                    loop = False

    # 리스트로 변환 후 반환
    boards = []
    for child in board_dict.keys():
        boards.append(board_dict[child])
    return boards

# 게시판 정보 가져오기
def select_board(board_id):

    # 게시판 확인
    bo = models.BOARD.objects.prefetch_related(
        'display_groups', 'write_groups', 'comment_groups'
    ).filter(
        id=board_id
    ).first()
    if not bo:
        return {
            'success': False,
            'message': '게시판 정보가 존재하지 않습니다.',
        }

    # 게시판 정보 포멧
    board = {
        'parent_board': None,
        'id': bo.id,
        'name': bo.name,
        'level_cut': bo.level_cut,
        'board_type': bo.board_type,
        'display_groups': [group.name for group in bo.display_groups.all()],
        'write_groups': [group.name for group in bo.write_groups.all()],
        'comment_groups': [group.name for group in bo.comment_groups.all()],
        'display_weight': bo.display_weight,
    }
    if bo.parent_board: # 상위 노드가 존재할 경우, 재귀적으로 상위 노드까지 가져옴
        board['parent_board'] = select_board(bo.parent_board.id)

    # board_ids 확인
    board['board_ids'] = str(board_id)
    if board['parent_board']:
        board['board_ids'] += ',' + board['parent_board']['board_ids']
        if board['parent_board']['parent_board']:
            board['board_ids'] += ',' + board['parent_board']['parent_board']['board_ids']
            if board['parent_board']['parent_board']['parent_board']:
                board['board_ids'] += ',' + board['parent_board']['parent_board']['parent_board']['board_ids']

    return board

# 게시판 생성
def create_board(name, board_type, display_groups, write_groups, comment_groups, level_cut, display_weight, parent_board_id=None):

    # 부모 게시판 확인
    if parent_board_id:
        parent_board = models.BOARD.objects.filter(
            id=parent_board_id
        ).first()
        if not parent_board:
            return {
                'success': False,
                'message': '부모 게시판 정보가 존재하지 않습니다.',
            }

    # 게시판 생성
    board = models.BOARD.objects.create(
        name=name,
        board_type=board_type,
        level_cut=level_cut,
        display_weight=display_weight,
    )
    if parent_board_id:
        board.parent_board = parent_board
    for display_group in str(display_groups).split(','):
        board.display_groups.add(display_group)
    for write_group in str(write_groups).split(','):
        board.write_groups.add(write_group)
    for comment_group in str(comment_groups).split(','):
        board.comment_groups.add(comment_group)

    return {
        'success': True,
        'message': '게시판이 생성되었습니다.',
        'pk': board.id,
    }

# 게시판 정보 업데이트
def update_board(board_id, name=None, board_type=None, display_groups=None, write_groups=None, comment_groups=None, level_cut=None, display_weight=None):

    # 게시판 확인
    board = models.BOARD.objects.prefetch_related(
        'display_groups', 'write_groups', 'comment_groups'
    ).filter(
        id=board_id
    ).first()
    if not board:
        return {
            'success': False,
            'message': '게시판 정보가 존재하지 않습니다.',
        }

    # 게시판 정보 업데이트
    if name: # 이름 업데이트
        board.name = name
    if board_type: # 게시판 타입 업데이트
        board.board_type = board_type
    if display_weight: # 노출 가중치 업데이트
        board.display_weight = display_weight
    if display_groups: # 조회 그룹 업데이트
        board.display_groups.clear()
        for display_group in str(display_groups).split(','):
            group = Group.objects.filter(
                name=display_group
            ).first()
            if group:
                board.display_groups.add(group)
    if write_groups:
        board.write_groups.clear()
        for write_group in str(write_groups).split(','):
            group = Group.objects.filter(
                name=write_group
            ).first()
            if group:
                board.write_groups.add(group)
    if comment_groups:
        board.comment_groups.clear()
        for comment_group in str(comment_groups).split(','):
            group = Group.objects.filter(
                name=comment_group
            ).first()
            if group:
                board.comment_groups.add(group)
    if level_cut:
        board.level_cut = level_cut
    board.save()

    return {
        'success': True,
        'message': '게시판 정보가 업데이트 되었습니다.',
        'pk': board.id,
    }

# 게시판 삭제 및 하위 게시판 초기화(cascade)
def delete_board(board_id):

    # 게시판 삭제
    board = models.BOARD.objects.filter(
        id=board_id
    ).first()

    # 게시판 삭제
    board.delete()

    return {
        'success': True,
        'message': '게시판이 삭제되었습니다.',
    }

# 카테고리 트리 생성
def make_category_tree():

    # 카테고리 확인
    categories = models.CATEGORY.objects.all().order_by('-display_weight')

    # 부모 카테고리가 없는 카테고리(최상위 카테고리)를 먼저 생성
    category_dict = {
        category.name: {
        'id': category.id,
        'name': category.name,
        'display_weight': category.display_weight,
        'children': [],
        'post_count': models.POST.objects.exclude(place_info__isnull=True).filter(place_info__categories__id__in=[category.id]).count(),
        } for category in categories if not category.parent_category
    }

    # 하위 카테고리 생성
    for category in categories:
        if category.parent_category: # 부모 카테고리가 존재할 경우,
            if category_dict.get(category.parent_category.name):
                category_dict[category.parent_category.name]['children'].append({
                'id': category.id,
                'name': category.name,
                'display_weight': category.display_weight,
                'children': [],
                'post_count': models.POST.objects.exclude(place_info__isnull=True).filter(place_info__categories__id__in=[category.id]).count(),
                })
        else:
            loop = True
            for key in category_dict.keys():
                for child in category_dict[key]['children']:
                    if not loop:
                        break
                    if child['name'] == category.parent_category.name:
                        child['children'].append({
                            'id': category.id,
                            'name': category.name,
                            'display_weight': category.display_weight,
                            'children': [],
                            'post_count': models.POST.objects.exclude(place_info__isnull=True).filter(place_info__categories__id__in=[category.id]).count(),
                        })
                        loop = False
                    if loop:
                        for grandchild in child['children']:
                            if not loop:
                                break
                            if grandchild['name'] == category.parent_category.name:
                                grandchild['children'].append({
                                    'id': category.id,
                                    'name': category.name,
                                    'display_weight': category.display_weight,
                                    'children': [],
                                    'post_count': models.POST.objects.exclude(place_info__isnull=True).filter(place_info__categories__id__in=[category.id]).count(),
                                })
                                loop = False

    # 리스트로 변환 후 반환
    categories = []
    for child in category_dict.keys():
        categories.append(category_dict[child])
    return categories

# 카테고리 정보 가져오기
def select_category(category_id):

    # 카테고리 확인
    category = models.CATEGORY.objects.filter(
        id=category_id
    ).first()
    if not category:
        return {
            'success': False,
            'message': '카테고리 정보가 존재하지 않습니다.',
        }

    # 카테고리 정보 포멧
    category_data = {
        'id': category.id,
        'name': category.name,
        'display_weight': category.display_weight,
    }
    if category.parent_category: # 상위 노드가 존재할 경우, 재귀적으로 상위 노드까지 가져옴
        category_data['parent_category'] = select_category(category.parent_category.id)

    # category_ids 확인
    category_data['category_ids'] = category_id
    if category_data.get('parent_category'):
        category_data['category_ids'] += ',' + category_data['parent_category']['category_ids']
        if category_data['parent_category'].get('parent_category'):
            category_data['category_ids'] += ',' + category_data['parent_category']['parent_category']['category_ids']
            if category_data['parent_category']['parent_category'].get('parent_category'):
                category_data['category_ids'] += ',' + category_data['parent_category']['parent_category']['parent_category']['category_ids']

    return category_data

# 카테고리 생성
def create_category(name, display_weight, parent_category_id=None):

    # 부모 카테고리 확인
    if parent_category_id:
        parent_category = models.CATEGORY.objects.filter(
            id=parent_category_id
        ).first()
        if not parent_category:
            return {
                'success': False,
                'message': '부모 카테고리 정보가 존재하지 않습니다.',
            }

    # 카테고리 생성
    category = models.CATEGORY.objects.create(
        name=name,
        display_weight=display_weight
    )
    if parent_category_id:
        category.parent_category = parent_category
        category.save()

    return {
        'success': True,
        'message': '카테고리가 생성되었습니다.',
    }

# 카테고리 정보 업데이트
def update_category(category_id, parent_category_id=None, name=None, display_weight=None):

    # 카테고리 확인
    category = models.CATEGORY.objects.filter(
        id=category_id
    ).first()
    if not category:
        return {
            'success': False,
            'message': '카테고리 정보가 존재하지 않습니다.',
        }

    # 부모 카테고리 확인
    if parent_category_id:
        parent_category = models.CATEGORY.objects.filter(
            id=parent_category_id
        ).first()
        if not parent_category:
            return {
                'success': False,
                'message': '부모 카테고리 정보가 존재하지 않습니다.',
            }

    # 카테고리 정보 업데이트
    if parent_category: # 부모 카테고리 업데이트
        category.parent_category = parent_category
    if name: # 이름 업데이트
        category.name = name
    if display_weight: # 노출 가중치 업데이트
        category.display_weight = display_weight

    return {
        'success': True,
        'message': '카테고리 정보가 업데이트 되었습니다.',
        'pk': category.id,
    }

# 카테고리 삭제 및 하위 카테고리 초기화(cascade)
def delete_category(category_id):

    # 카테고리 삭제
    category = models.CATEGORY.objects.filter(
        id=category_id
    ).first()

    # 카테고리 삭제
    category.delete()

    return {
        'success': True,
        'message': '카테고리가 삭제되었습니다.',
    }
