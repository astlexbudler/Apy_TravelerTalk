import datetime
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
아래 dao 함수들에 대해서는 권한을 확인할 필요는 없음. 권한 확인은 views에서 처리
page 파라메터를 받는 함수들은 반환 시 last_page도 함께 반환(페이지네이션을 위함) 예: return activities, last_page
##### [ACCOUNT]
get_default_contexts(request): 기본 컨텍스트 정보 가져오기
    - account, activities_preview, unread_messages, coupons_preview, best_reviews, server_settings 정보를 가져옴.
    - 각 항목은 사용자 정보, 사용자 활동 내역, 받은 메세지, 내 쿠폰, 베스트 리뷰, 서버 설정 정보로 구성됨.

get_urls(): URL 정보 가져오기

select_account(account_id): 사용자 정보 가져오기
    - username(로그인 아이디), nickname(first_name 닉네임), partner_name(last_name 파트너 이름), email, group(그룹), status(상태), subsupervisor_permissions(부관리자 권한), level(레벨), exp(경험치), mileage(마일리지) 반환.
    - level 정보에는 level(레벨), image(레벨 이미지), text(레벨 텍스트), text_color(텍스트 색상), background_color(배경 색상) 포함.

select_account_detail(account_id): 사용자 상세 정보 가져오기(모든 정보)
    - select_account 정보를 포함하며 추가로 note(메모) 반환.

create_account(username, password, first_name, last_name, email, tel, account_type): 사용자 생성
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

delete_place_info(post_id): 게시글의 여행지 정보 삭제

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
select_all_coupons(code=None, name=None, status=None): 모든 쿠폰 가져오기
    - status에 따라 쿠폰 필터링.
    - code, related_post, name, content, image, expire_at, required_mileage, own_accounts, status 반환.

select_coupon(coupon_id): 쿠폰 정보 가져오기
select_created_coupons(account_id, status=None): 사용자가 생성한 쿠폰 가져오기
select_owned_coupons(account_id, status=None): 사용자가 소유한 쿠폰 가져오기
    - status로 필터링하여 쿠폰 반환.

create_coupon(account_id, code, related_post_id, name, content, image, expire_at, required_mileage): 쿠폰 생성
update_coupon(coupon_id, data): 쿠폰 정보 업데이트

##### [MESSAGE]
select_message(message_id): 메세지 정보 가져오기
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
create_statistic(name, date, value): 통계 생성

##### [BLOCKED_IP]
select_blocked_ips(): 차단된 IP 목록 가져오기
create_blocked_ip(data): IP 차단
delete_blocked_ip(ip): IP 차단 해제

##### [BOARD & CATEGORY TREE]
make_board_tree(group_name): 게시판 트리 생성
make_board_tree_all(): 모든 게시판 트리 생성
make_travel_board_tree(): 여행지 게시판 트리 생성
select_board(board_id): 게시판 정보 가져오기
create_board(data): 게시판 생성
update_board(board_id, data): 게시판 업데이트
delete_board(board_id): 게시판 삭제

make_category_tree(): 카테고리 트리 생성
select_category(category_id): 카테고리 정보 가져오기
create_category(parent_id, name, display_weight): 카테고리 생성
update_category(category_id, parnter_id, name, display_weight): 카테고리 업데이트
delete_category(category_id): 카테고리 삭제
"""



##### [ACCOUNT]
# 기본 컨텍스트 정보 가져오기
def get_default_contexts(request):

    # 사용자 정보 확인
    if not request.user.is_authenticated:
        guest_id = request.session.get('guest_id', 'guest_'.join(random.choices(string.ascii_letters + string.digits, k=8)))
        request.session['guest_id'] = guest_id
        account = {
            'id': guest_id,
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

        # 사용자 활동 내역 확인
        activities_preview = select_account_activities(account['id'], page=1)[0][:5]

        # 받은 메세지 확인
        messages = models.MESSAGE.objects.filter(
            to_account=account['id'],
            is_read=False
        )
        unread_messages = []
        for message in messages:
            if message.sender_account == 'supervisor':
                sender = {
                    'id': 'supervisor',
                    'nickname': '관리자',
                }
            elif message.sender_account == 'guest':
                sender = {
                    'id': 'guest',
                    'nickname': '게스트',
                }
            else:
                sender = models.ACCOUNT.objects.filter(
                    id=message.sender_account
                ).first()
                if sender:
                    sender = {
                        'id': sender.id,
                        'nickname': sender.first_name,
                    }
                else:
                    sender = {
                        'id': '',
                        'nickname': '없는 사용자',
                    }
            unread_messages.append({
                'id': message.id,
                'title': message.title,
                'sender': sender,
                'created_at': datetime.datetime.strftime(message.created_at, '%Y-%m-%d %H:%M'),
            })

        # 내 쿠폰 확인
        coupons_preview = models.COUPON.objects.select_related(
            'own_account'
        ).filter(
            own_account__id=account['id']
        ).order_by('-created_at')[:5]

        # 베스트 리뷰 확인
        review_board = models.BOARD.objects.filter(
            board_type='review'
        ).first()
        best_reviews = search_posts(order='best', page=1, board_id=review_board.id)[0][:5]

        # 즐겨찾기
        bookmarks = select_account_bookmarked_posts(account['id'])[:5]

    # 서버 설정 정보 확인
    server_settings = {
        'site_logo': select_server_setting('site_logo'),
        'service_name': select_server_setting('service_name'),
        'site_header': select_server_setting('site_header'),
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
        'main_url': settings.MAIN_URL,
        'supervisor_url': settings.SUPERVISOR_URL,
        'partner_url': settings.PARTNER_URL,
    }

# 사용자 정보 가져오기
def select_account(account_id):

    # 사용자 정보 확인
    account = models.ACCOUNT.objects.select_related(
        'level'
    ).prefetch_related(
        'bookmarked_posts', 'groups'
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
        'bookmarked_posts', 'groups'
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
            'tel': account.tel,
            'account_type': account.groups.all()[0].name, # 각 계정은 하나의 그룹만 가짐
            'status': account.status,
            'subsupervisor_permissions': str(account.subsupervisor_permissions).split(','),
            'level': select_level(account.level.level),
            'bookmarked_posts': [post.id for post in account.bookmarked_posts.all()],
            'exp': account.exp,
            'mileage': account.mileage,
            'note': account.note,
            'created_at': datetime.datetime.strftime(account.date_joined, '%Y-%m-%d %H:%M'),
            'last_login': datetime.datetime.strftime(account.last_login, '%Y-%m-%d %H:%M') if account.last_login else None,
        }
    else: # 사용자 정보가 없는 경우
        return None

# 사용자 생성
def create_account(username, password, first_name, last_name, email, tel, account_type):

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
        tel=tel,
    )
    account.set_password(password)
    account.save()
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

    default_level = models.LEVEL_RULE.objects.get(level=1)
    account.level = default_level
    account.save()

    return {
        'success': True,
        'message': '사용자가 생성되었습니다.',
        'pk': account.id,
        'status': account.status,
    }

# 사용자 정보 업데이트
def update_account(account_id, password=None, first_name=None, last_name=None, email=None, status=None, note=None, subsupervisor_permissions=None, exp=None, mileage=None, recent_ip=None):

    # 사용자 정보 확인
    account = models.ACCOUNT.objects.select_related(
        'level'
    ).filter(
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
def search_posts(title=None, category_id=None, board_id=None, related_post_id=None, order='default', page=1, post_type='default'):

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
def select_post(post_id):

    # 게시글 정보 확인
    post = models.POST.objects.select_related(
        'author', 'related_post', 'place_info'
    ).prefetch_related(
        'boards', 'place_info__categories', 'boards__comment_groups'
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
            'id': post.author.id,
            'nickname': post.author.last_name,
            'partner_name': post.author.first_name,
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
def create_post(author_id, title, content, board_ids, related_post_id=None, image=None):

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
        address=address,
    )
    place_info.categories.set(categories)
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
        'author', 'author__level'
    ).filter(
        post=post.first()
    )

    # 게시글 댓글 포멧
    comments_data = [{
        'id': comment.id,
        'author': {
            'id': comment.author.id,
            'nickname': comment.author.first_name,
            'partner_name': comment.author.last_name,
            'level': select_level(comment.author.level.level),
        },
        'content': comment.content,
        'created_at': datetime.datetime.strftime(comment.created_at, '%Y-%m-%d %H:%M'),
    } for comment in comments]

    return comments_data

# 댓글 생성
def create_comment(post_id, account_id, content):

    # 게시글 확인
    post = models.POST.objects.filter(
        id=post_id
    ).first()
    if not post:
        return {
            'success': False,
            'message': '게시글 정보가 존재하지 않습니다.',
        }

    # 사용자 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    ).first()
    if not account:
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 댓글 생성
    comment = models.COMMENT.objects.create(
        post=post,
        author=account,
        content=content,
    )

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
def select_all_coupons(code=None, name=None, status=None):

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
    if status:
        query &= Q(status=status)

    coupons = coupons.filter(query)

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

    return coupons_data

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

# 사용자가 생성한 쿠폰 정보 가져오기
def select_created_coupons(account_id, status=None, page=1):

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
        'own_account', 'related_post', 'create_account', 'own_account__level',
    ).prefetch_related(
        'create_account__groups'
    )

    # 상태에 따라 필터링
    if status == 'active':
        coupons = coupons.filter(
            create_account=account.first(),
            status='active'
        )
    else:
        coupons = coupons.exclude(
            status='active'
        ).filter(
            create_account=account.first()
        )

    # 정렬
    coupons = coupons.order_by('-created_at')

    # 페이지네이션
    last_page = (coupons.count() // 20) + 1
    coupons = coupons[(page-1)*20:page*20]

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

    return coupons_data , last_page

# 사용자가 소유한 쿠폰 정보 가져오기
def select_owned_coupons(account_id, status=None, page=1):

    # 사용자 확인
    account = models.ACCOUNT.objects.filter(
        id=account_id
    ).first()
    if not account:
        return {
            'success': False,
            'message': '사용자 정보가 존재하지 않습니다.',
        }

    # 사용자가 소유한 쿠폰 정보 확인
    coupons = models.COUPON.objects.select_related(
        'own_account', 'related_post', 'create_account', 'own_account__level',
    ).prefetch_related(
        'create_account__groups'
    )

    if status == 'active':
        coupons = coupons.filter(
            own_account=account,
            status='active'
        )
    else:
        coupons = coupons.exclude(
            status='active'
        ).filter(
            own_account=account
        )

    # 정렬
    coupons = coupons.order_by('-created_at')

    # 페이지네이션
    last_page = (coupons.count() // 20) + 1
    coupons = coupons[(page-1)*20:page*20]

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
        'include_coupon'
    ).filter(
        id=message_id
    ).first()
    if not message:
        return {
            'success': False,
            'message': '메세지 정보가 존재하지 않습니다.',
        }

    # 보낸 사람 정보
    if message.sender_account == 'supervisor':
        from_account = {
            'id': 'supervisor',
            'nickname': '관리자',
        }
    elif str(message.sender_account).startswith('guest'):
        from_account = {
            'id': message.sender_account,
            'nickname': f'손님({message.sender_account})',
        }
    else:
        from_account = models.ACCOUNT.objects.filter(
            id=message.sender_account
        ).first()
        if not from_account:
            from_account = {
                'id': '',
                'nickname': '없는 사용자',
            }
        else:
            from_account = {
                'id': from_account.id,
                'nickname': from_account.first_name,
            }

    # 받는 사람 정보
    if message.to_account == 'supervisor':
        to_account = {
            'id': 'supervisor',
            'nickname': '관리자',
        }
    elif str(message.to_account).startswith('guest'):
        to_account = {
            'id': message.to_account,
            'nickname': f'손님({message.to_account})',
        }
    else:
        to_account = models.ACCOUNT.objects.filter(
            id=message.to_account
        ).first()
        if not to_account:
            to_account = {
                'id': '',
                'nickname': '없는 사용자',
            }
        else:
            to_account = {
                'id': to_account.id,
                'nickname': to_account.first_name,
            }

    # 메세지 정보 포멧
    message_data = {
        'id': message.id,
        'sender_account': from_account,
        'to_account': to_account,
        'title': message.title,
        'content': message.content,
        'image': '/media/' + str(message.image) if message.image else None,
        'include_coupon': {
            'code': message.include_coupon.code,
            'name': message.include_coupon.name,
        } if message.include_coupon else None,
        'is_read': message.is_read,
        'created_at': datetime.datetime.strftime(message.created_at, '%Y-%m-%d %H:%M'),
    }

    return message_data

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
    messages = models.MESSAGE.objects.select_related(
        'include_coupon'
    ).filter(
        to_account=account_id
    )

    # 정렬
    messages = messages.order_by('-created_at')

    # 페이지네이션
    last_page = (messages.count() // 20) + 1
    messages = messages[(page-1)*20:page*20]
    messages_data = []

    # 메세지 정보 포멧
    for message in messages:

        # 보낸 사람 정보
        if message.sender_account == 'supervisor':
            from_account = {
                'id': 'supervisor',
                'nickname': '관리자',
            }
        elif str(message.sender_account).startswith('guest'):
            from_account = {
                'id': message.sender_account,
                'nickname': f'손님({message.sender_account})',
            }
        else:
            from_account = models.ACCOUNT.objects.filter(
                id=message.sender_account
            ).first()
            if not from_account: # supervisor or guest_id
                from_account = {
                    'id': '',
                    'nickname': '없는 사용자',
                }
            else:
                from_account = {
                    'id': from_account.id,
                    'nickname': from_account.first_name,
                }

        # 메세지 포멧
        messages_data.append({
            'id': message.id,
            'sender_account': from_account,
            'title': message.title,
            'content': message.content,
            'image': '/media/' + str(message.image) if message.image else None,
            'include_coupon': {
                'code': message.include_coupon.code,
                'name': message.include_coupon.name,
            } if message.include_coupon else None,
            'is_read': message.is_read,
            'created_at': datetime.datetime.strftime(message.created_at, '%Y-%m-%d %H:%M'),
        })

    return messages_data, last_page

# 사용자가 보낸 메세지 가져오기
def select_sent_messages(account_id, page=1):

    # 사용자 확인
    if account_id == 'supervisor':
        account = {
            'id': 'supervisor',
            'nickname': '관리자',
        }
    elif str(account_id).startswith('guest'):
        account = {
            'id': account_id,
            'nickname': f'손님({account_id})',
        }
    else:
        account = models.ACCOUNT.objects.filter(
            id=account_id
        ).first()
        if not account:
            return {
                'success': False,
                'message': '사용자 정보가 존재하지 않습니다.',
            }
        account = {
            'id': account.id,
            'nickname': account.first_name,
        }

    # 사용자가 보낸 메세지 확인
    messages = models.MESSAGE.objects.select_related(
        'include_coupon'
    ).filter(
        sender_account=account['id']
    )

    # 정렬
    messages = messages.order_by('-created_at')

    # 페이지네이션
    last_page = (messages.count() // 20) + 1
    messages = messages[(page-1)*20:page*20]
    messages_data = []

    # 메세지 정보 포멧
    for message in messages:

        try:
            # 받는 사람 정보
            if message.to_account == 'supervisor':
                to_account = {
                    'id': 'supervisor',
                    'nickname': '관리자',
                }
            elif str(message.to_account).startswith('guest'):
                to_account = {
                    'id': account_id,
                    'nickname': f'손님({message.to_account})',
                }
            else:
                to_account = models.ACCOUNT.objects.filter(
                    id=message.to_account
                ).first()
                if not to_account:
                    to_account = {
                        'id': '',
                        'nickname': '없는 사용자',
                    }
                else:
                    to_account = {
                        'id': to_account.id,
                        'nickname': to_account.first_name,
                    }
            # 메세지 포멧
            messages_data.append({
                'id': message.id,
                'to_account': to_account,
                'title': message.title,
                'content': message.content,
                'image': '/media/' + str(message.image) if message.image else None,
                'include_coupon': {
                    'code': message.include_coupon_code,
                    'name': message.include_coupon.name,
                } if message.include_coupon else None,
                'is_read': message.is_read,
                'created_at': datetime.datetime.strftime(message.created_at, '%Y-%m-%d %H:%M'),
            })
        except Exception as e:
            message.delete()

    return messages_data, last_page

# 메세지 생성
def create_message(sender_id, receiver_id, title, content, image, include_coupon_code):

    # 쿠폰 확인
    coupon = None
    if include_coupon_code:
        coupon = models.COUPON.objects.filter(
            code=include_coupon_code
        )
        if coupon.exists():
            coupon = coupon.first()

    # 메세지 생성
    message = models.MESSAGE.objects.create(
        sender_account=sender_id,
        to_account=receiver_id,
        title=title,
        content=content,
        image=image,
        include_coupon=coupon,
    )

    return {
        'success': True,
        'message': '메세지가 생성되었습니다.',
        'pk': message.id,
    }

# 메세지 정보 업데이트(읽음 처리)
def update_message(message_id, delete_coupon=False):

    # 메세지 확인
    message = models.MESSAGE.objects.filter(
        id=message_id
    )
    if not message.exists():
        return {
            'success': False,
            'message': '메세지 정보가 존재하지 않습니다.',
        }

    # 메세지 업데이트
    message = message.first()
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
def select_all_server_settings():

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
def select_banners():

    # 모든 배너 정보 확인
    banners = models.BANNER.objects.all()

    # 배너 정보 포멧
    banner_data = {
        'top': [],
        'side': [],
    }
    for banner in banners:
        if banner.location == 'top':
            banner_data['top'].append({
                'id': banner.id,
                'image': '/media/' + str(banner.image) if banner.image else None,
                'link': banner.link,
                'display_weight': banner.display_weight,
                'location': banner.location,
                'size': banner.size,
            })
        else:
            banner_data['side'].append({
                'id': banner.id,
                'image': '/media/' + str(banner.image) if banner.image else None,
                'link': banner.link,
                'display_weight': banner.display_weight,
                'location': banner.location,
                'size': banner.size,
            })

    return banner_data

# 배너 생성
def create_banner(image, link, display_weight, location, size):

    # 배너 생성
    banner = models.BANNER.objects.create(
        image=image,
        link=link,
        display_weight=display_weight,
        location=location,
        size=size,
    )

    return {
        'success': True,
        'message': '배너가 생성되었습니다.',
        'pk': banner.id,
    }

# 배너 정보 업데이트
def update_banner(banner_id, image=None, link=None, display_weight=None, location=None, size=None):

    # 배너 확인
    banner = models.BANNER.objects.filter(
        id=banner_id
    )
    if not banner.exists():
        return {
            'success': False,
            'message': '배너 정보가 존재하지 않습니다.',
        }

    # 배너 정보 업데이트
    banner = banner.first()
    if image: # 이미지 업데이트
        banner.image = image
    if link: # 링크 업데이트
        banner.link = link
    if display_weight: # 노출 가중치 업데이트
        banner.display_weight = display_weight
    if location: # 위치 업데이트
        banner.location = location
    if size: # 크기 업데이트
        banner.size = size
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
def create_statistic(name, date=datetime.datetime.now(), value=1):

    # 통계 생성
    exist = models.STATISTIC.objects.filter(
        name=name,
        date=date
    )
    if exist.exists():
        exist.first().value += 1
        exist.first().save()
    else:
        models.STATISTIC.objects.create(
            name=name,
            value=value,
            date=date,
        )

    return {
        'success': True,
        'message': '통계가 생성되었습니다.',
    }



##### [BLOCKED_IP]
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
def make_board_tree(group_name):

    # 게시판 확인
    boards = models.BOARD.objects.prefetch_related(
        'display_groups', 'enter_groups', 'write_groups', 'comment_groups'
    ).filter(
        #Q(display_groups__name__in=[group_name])
    ).order_by('-display_weight')
    for board in boards:
        print(board.name)
    board_dict = { # 부모 게시판이 없는 게시판(최상위 게시판)을 먼저 생성
        board.name: {
            'id': board.id,
            'name': board.name,
            'board_type': board.board_type,
            'children': [],
        } for board in boards if not board.parent_board
    }
    for board in boards:
        if board.parent_board: # 부모 게시판이 존재할 경우,
            if board_dict.get(board.parent_board.name): # 부모 게시판의 자식으로 추가
                children = {
                    'id': board.id,
                    'name': board.name,
                    'board_type': board.board_type,
                    'children': [],
                }
                if children not in board_dict[board.parent_board.name]['children']:
                    board_dict[board.parent_board.name]['children'].append(children)
            else: # 부모 게시판이 없을 경우, 3차 이상의 노드들
                loop = True
                for key in board_dict.keys(): # 부모 게시판의 자식의 자식 확인...
                    for child in board_dict[key]['children']:
                        if not loop:
                            break
                        if str(child['name']) == str(board.parent_board.name):
                            children = {
                                'id': board.id,
                                'name': board.name,
                                'board_type': board.board_type,
                                'children': [],
                            }
                            if children not in child['children']:
                                child['children'].append(children)
                                loop = False
                        if loop:
                            for grandchild in child['children']:
                                if not loop:
                                    break
                                if str(grandchild['name']) == str(board.parent_board.name):
                                    children = {
                                        'id': board.id,
                                        'name': board.name,
                                        'board_type': board.board_type,
                                        'children': [],
                                    }
                                    if children not in grandchild['children']:
                                        grandchild['children'].append({
                                            'id': board.id,
                                            'name': board.name,
                                            'board_type': board.board_type,
                                            'children': [],
                                        })
                                        loop = False
    boards = []
    for child in board_dict.keys():
        boards.append(board_dict[child])
    print(boards)
    return boards

# 모든 게시판 트리 생성
def make_board_tree_all():

    # 게시판 확인
    boards = models.BOARD.objects.prefetch_related(
        'display_groups', 'enter_groups', 'write_groups', 'comment_groups'
    ).all().order_by('-display_weight')
    board_dict = {
        board.name: {
            'id': board.id,
            'name': board.name,
            'board_type': board.board_type,
            'display_groups': [group.name for group in board.display_groups.all()],
            'enter_groups': [group.name for group in board.enter_groups.all()],
            'write_groups': [group.name for group in board.write_groups.all()],
            'comment_groups': [group.name for group in board.comment_groups.all()],
            'level_cut': board.level_cut,
            'post_count': models.POST.objects.prefetch_related('boards').filter(boards__id__in=[board.id]).count(),
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
                    'display_groups': [group.name for group in board.display_groups.all()],
                    'enter_groups': [group.name for group in board.enter_groups.all()],
                    'write_groups': [group.name for group in board.write_groups.all()],
                    'comment_groups': [group.name for group in board.comment_groups.all()],
                    'level_cut': board.level_cut,
                    'post_count': models.POST.objects.prefetch_related('boards').filter(boards__id__in=[board.id]).count(),
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
                                'display_groups': [group.name for group in board.display_groups.all()],
                                'enter_groups': [group.name for group in board.enter_groups.all()],
                                'write_groups': [group.name for group in board.write_groups.all()],
                                'comment_groups': [group.name for group in board.comment_groups.all()],
                                'level_cut': board.level_cut,
                                'post_count': models.POST.objects.prefetch_related('boards').filter(boards__id__in=[board.id]).count(),
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
                                        'display_groups': [group.name for group in board.display_groups.all()],
                                        'enter_groups': [group.name for group in board.enter_groups.all()],
                                        'write_groups': [group.name for group in board.write_groups.all()],
                                        'comment_groups': [group.name for group in board.comment_groups.all()],
                                        'level_cut': board.level_cut,
                                        'post_count': models.POST.objects.prefetch_related('boards').filter(boards__id__in=[board.id]).count(),
                                        'children': [],
                                    })
                                    loop = False
    boards = []
    for child in board_dict.keys():
        boards.append(board_dict[child])

    return boards

# 여행지 게시판 생성
def make_travel_board_tree():

    # 그룹 게시판 확인
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

    # 게시판 확인
    boards = models.BOARD.objects.filter(
        Q(board_type='travel') | Q(board_type='tree') # 여행지 게시판 또는 트리
    ).order_by('-display_weight')
    board_dict = {
        board.name: {
            'id': board.id,
            'name': board.name,
            'board_type': board.board_type,
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
                                        'children': [],
                                    })
                                    loop = False
    boards = []
    for child in board_dict.keys():
        boards.append(board_dict[child])
    boards = remove_empty_tree_nodes(boards)

    return boards

# 게시판 정보 가져오기
def select_board(board_id):

    # 게시판 확인
    board = models.BOARD.objects.select_related(
        'parent_board'
    ).prefetch_related(
        'display_groups', 'enter_groups', 'write_groups', 'comment_groups'
    ).filter(
        id=board_id
    ).first()
    if not board:
        return {
            'success': False,
            'message': '게시판 정보가 존재하지 않습니다.',
        }

    # 만약 상위 노드가 있는지 확인
    ids = [board.id]
    if board.parent_board:
        parent_board = models.BOARD.objects.select_related(
            'parent_board'
        ).filter(
            id=board.parent_board.id
        ).first()
        if parent_board:
            ids.append(parent_board.id)
            if parent_board.parent_board:
                grandparent_board = models.BOARD.objects.select_related(
                    'parent_board'
                ).filter(
                    id=parent_board.parent_board.id
                ).first()
                if grandparent_board:
                    ids.append(grandparent_board.id)
                    if grandparent_board.parent_board:
                        great_grandparent_board = models.BOARD.objects.select_related(
                            'parent_board'
                        ).filter(
                            id=grandparent_board.parent_board.id
                        ).first()
                        if great_grandparent_board:
                            ids.append(great_grandparent_board.id)

    # 게시판 정보 포멧
    board_data = {
        'id': board.id,
        'name': board.name,
        'board_type': board.board_type,
        'display_groups': [group.name for group in board.display_groups.all()],
        'enter_groups': [group.name for group in board.enter_groups.all()],
        'write_groups': [group.name for group in board.write_groups.all()],
        'comment_groups': [group.name for group in board.comment_groups.all()],
        'level_cut': board.level_cut,
        'ids': ids,
    }

    return board_data

# 게시판 생성
def create_board(name, board_type, display_groups, enter_groups, write_groups, comment_groups, level_cut, display_weight, parent_board_id=None):

    # 게시판 생성
    board = models.BOARD.objects.create(
        parent_board_id=parent_board_id,
        name=name,
        board_type=board_type,
        level_cut=level_cut,
        display_weight=display_weight,
    )
    for display_group in display_groups:
        board.display_groups.add(display_group)
    for enter_group in enter_groups:
        board.enter_groups.add(enter_group)
    for write_group in write_groups:
        board.write_groups.add(write_group)
    for comment_group in comment_groups:
        board.comment_groups.add(comment_group)

    return {
        'success': True,
        'message': '게시판이 생성되었습니다.',
        'pk': board.id,
    }

# 게시판 정보 업데이트
def update_board(board_id, parent_board_id=None, name=None, board_type=None, display_groups=None, enter_groups=None, write_groups=None, comment_groups=None, level_cut=None, display_weight=None):

    # 게시판 확인
    board = models.BOARD.objects.prefetch_related(
        'display_groups', 'enter_groups', 'write_groups', 'comment_groups'
    ).filter(
        id=board_id
    )
    if not board.exists():
        return {
            'success': False,
            'message': '게시판 정보가 존재하지 않습니다.',
        }

    # 게시판 정보 업데이트
    board = board.first()
    if parent_board_id: # 상위 게시판 업데이트
        board.parent_board_id = parent_board_id
    if name: # 이름 업데이트
        board.name = name
    if board_type: # 게시판 타입 업데이트
        board.board_type = board_type
    if display_weight: # 노출 가중치 업데이트
        board.display_weight = display_weight
    if display_groups: # 조회 그룹 업데이트
        board.display_groups.clear()
        for display_group in board.display_groups.all():
            group = Group.objects.filter(
                name=display_group
            ).first()
            if group:
                board.display_groups.add(group)
    if enter_groups:
        board.enter_groups.clear()
        for enter_group in board.enter_groups.all():
            group = Group.objects.filter(
                name=enter_group
            ).first()
            if group:
                board.enter_groups.add(group)
    if write_groups:
        board.write_groups.clear()
        for write_group in board.write_groups.all():
            group = Group.objects.filter(
                name=write_group
            ).first()
            if group:
                board.write_groups.add(group)
    if comment_groups:
        board.comment_groups.clear()
        for comment_group in board.comment_groups.all():
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

# 게시판 삭제 및 하위 게시판 초기화
def delete_board(board_id):

    # 게시판 삭제
    board = models.BOARD.objects.filter(
        id=board_id
    ).first()

    # 이 노드를 부모로 가지는 모든 노드 삭제
    models.BOARD.objects.filter(
        parent_board_id=board_id
    ).delete()

    # 게시판 삭제
    board.delete()

    return {
        'success': True,
        'message': '게시판이 삭제되었습니다.',
    }

# 카테고리 트리 생성
def make_category_tree():
    categories = models.CATEGORY.objects.select_related('parent_category').all().order_by('-display_weight')
    category_dict = {
        category.name: {
        'id': str(category.id),
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
                'id': str(category.id),
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
                            'id': str(category.id),
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
                                    'id': str(category.id),
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

# 카테고리 정보 가져오기
def select_category(category_id):

    # 카테고리 확인
    category = models.CATEGORY.objects.select_related(
        'parent_category'
    ).filter(
        id=category_id
    ).first()
    if not category:
        return {
            'success': False,
            'message': '카테고리 정보가 존재하지 않습니다.',
        }

    # 부모 카테고리 정보
    ids = [category.id]
    if category.parent_category:
        parent_category = models.CATEGORY.objects.filter(
            id=category.parent_category.id
        ).first()
        if parent_category:
            ids.append(parent_category.id)
            if parent_category.parent_category:
                grandparent_category = models.CATEGORY.objects.filter(
                    id=parent_category.parent_category.id
                ).first()
                if grandparent_category:
                    ids.append(grandparent_category.id)
                    if grandparent_category.parent_category:
                        great_grandparent_category = models.CATEGORY.objects.filter(
                            id=grandparent_category.parent_category.id
                        ).first()
                        if great_grandparent_category:
                            ids.append(great_grandparent_category.id)

    # 카테고리 정보 포멧
    category_data = {
        'id': category.id,
        'name': category.name,
        'display_weight': category.display_weight,
        'ids': ids,
    }

    return category_data

# 카테고리 생성
def create_category(name, display_weight, parent_category_id=None):

    # 부모 카테고리 확인
    parent_category = None
    if parent_category_id:
        parent_category = models.CATEGORY.objects.filter(
            id=parent_category_id
        )
        if not parent_category.exists():
            return {
                'success': False,
                'message': '부모 카테고리 정보가 존재하지 않습니다.',
            }

    # 카테고리 생성
    models.CATEGORY.objects.create(
        parent_category=parent_category.first() if parent_category else None,
        name=name,
        display_weight=display_weight
    )

    return {
        'success': True,
        'message': '카테고리가 생성되었습니다.',
    }

# 카테고리 정보 업데이트
def update_category(category_id, parent_category_id=None, name=None, display_weight=None):

    # 카테고리 확인
    category = models.CATEGORY.objects.filter(
        id=category_id
    )
    if not category.exists():
        return {
            'success': False,
            'message': '카테고리 정보가 존재하지 않습니다.',
        }

    # 부모 카테고리 확인
    parent_category = None
    if parent_category_id:
        parent_category = models.CATEGORY.objects.filter(
            id=parent_category_id
        )
        if not parent_category.exists():
            return {
                'success': False,
                'message': '부모 카테고리 정보가 존재하지 않습니다.',
            }

    # 카테고리 정보 업데이트
    category = category.first()
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

# 카테고리 삭제 및 하위 카테고리 초기화
def delete_category(category_id):

    # 카테고리 삭제
    category = models.CATEGORY.objects.filter(
        id=category_id
    ).first()

    # 이 노드를 부모로 가지는 모든 노드 삭제
    models.CATEGORY.objects.filter(
        parent_category=category
    ).delete()

    # 카테고리 삭제
    category.delete()

    return {
        'success': True,
        'message': '카테고리가 삭제되었습니다.',
    }
